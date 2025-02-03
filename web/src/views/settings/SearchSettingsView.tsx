import Heading from "@/components/ui/heading";
import { FrigateConfig, SearchModelSize } from "@/types/frigateConfig";
import useSWR from "swr";
import axios from "axios";
import ActivityIndicator from "@/components/indicators/activity-indicator";
import { useCallback, useContext, useEffect, useState } from "react";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Toaster } from "@/components/ui/sonner";
import { toast } from "sonner";
import { Separator } from "@/components/ui/separator";
import { Link } from "react-router-dom";
import { LuExternalLink } from "react-icons/lu";
import { StatusBarMessagesContext } from "@/context/statusbar-provider";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
} from "@/components/ui/select";

type SearchSettingsViewProps = {
  setUnsavedChanges: React.Dispatch<React.SetStateAction<boolean>>;
};

type SearchSettings = {
  enabled?: boolean;
  reindex?: boolean;
  model_size?: SearchModelSize;
};

export default function SearchSettingsView({
  setUnsavedChanges,
}: SearchSettingsViewProps) {
  const { data: config, mutate: updateConfig } =
    useSWR<FrigateConfig>("config");
  const [changedValue, setChangedValue] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const { addMessage, removeMessage } = useContext(StatusBarMessagesContext)!;

  const [searchSettings, setSearchSettings] = useState<SearchSettings>({
    enabled: undefined,
    reindex: undefined,
    model_size: undefined,
  });

  const [origSearchSettings, setOrigSearchSettings] = useState<SearchSettings>({
    enabled: undefined,
    reindex: undefined,
    model_size: undefined,
  });

  useEffect(() => {
    if (config) {
      if (searchSettings?.enabled == undefined) {
        setSearchSettings({
          enabled: config.semantic_search.enabled,
          reindex: config.semantic_search.reindex,
          model_size: config.semantic_search.model_size,
        });
      }

      setOrigSearchSettings({
        enabled: config.semantic_search.enabled,
        reindex: config.semantic_search.reindex,
        model_size: config.semantic_search.model_size,
      });
    }
    // we know that these deps are correct
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [config]);

  const handleSearchConfigChange = (newConfig: Partial<SearchSettings>) => {
    setSearchSettings((prevConfig) => ({ ...prevConfig, ...newConfig }));
    setUnsavedChanges(true);
    setChangedValue(true);
  };

  const saveToConfig = useCallback(async () => {
    setIsLoading(true);

    axios
      .put(
        `config/set?semantic_search.enabled=${searchSettings.enabled ? "True" : "False"}&semantic_search.reindex=${searchSettings.reindex ? "True" : "False"}&semantic_search.model_size=${searchSettings.model_size}`,
        {
          requires_restart: 0,
        },
      )
      .then((res) => {
        if (res.status === 200) {
          toast.success("已保存搜索设置。", {
            position: "top-center",
          });
          setChangedValue(false);
          updateConfig();
        } else {
          toast.error(`F无法保存配置更改：${res.statusText}`, {
            position: "top-center",
          });
        }
      })
      .catch((error) => {
        toast.error(
          `无法保存配置更改：${error.response.data.message}`,
          { position: "top-center" },
        );
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, [
    updateConfig,
    searchSettings.enabled,
    searchSettings.reindex,
    searchSettings.model_size,
  ]);

  const onCancel = useCallback(() => {
    setSearchSettings(origSearchSettings);
    setChangedValue(false);
    removeMessage("search_settings", "search_settings");
  }, [origSearchSettings, removeMessage]);

  useEffect(() => {
    if (changedValue) {
      addMessage(
        "search_settings",
        `Unsaved search settings changes`,
        undefined,
        "search_settings",
      );
    } else {
      removeMessage("search_settings", "search_settings");
    }
    // we know that these deps are correct
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [changedValue]);

  useEffect(() => {
    document.title = "搜索设置 - Frigate";
  }, []);

  if (!config) {
    return <ActivityIndicator />;
  }

  return (
    <div className="flex size-full flex-col md:flex-row">
      <Toaster position="top-center" closeButton={true} />
      <div className="scrollbar-container order-last mb-10 mt-2 flex h-full w-full flex-col overflow-y-auto rounded-lg border-[1px] border-secondary-foreground bg-background_alt p-2 md:order-none md:mb-0 md:mr-2 md:mt-0">
        <Heading as="h3" className="my-2">
          搜索设置
        </Heading>
        <Separator className="my-2 flex bg-secondary" />
        <Heading as="h4" className="my-2">
          相似度搜索
        </Heading>
        <div className="max-w-6xl">
          <div className="mb-5 mt-2 flex max-w-5xl flex-col gap-2 text-sm text-primary-variant">
            <p>
              通过 Frigate 中的语义搜索功能，您可以使用图像本身、用户定义的文本描述或自动生成的文本描述，在审核项中查找跟踪到的目标。
            </p>

            <div className="flex items-center text-primary">
              <Link
                to="https://c4s.tech/docs/Frigate/configuration/semantic_search"
                target="_blank"
                rel="noopener noreferrer"
                className="inline"
              >
                阅读文档
                <LuExternalLink className="ml-2 inline-flex size-3" />
              </Link>
            </div>
          </div>
        </div>

        <div className="flex w-full max-w-lg flex-col space-y-6">
          <div className="flex flex-row items-center">
            <Switch
              id="enabled"
              className="mr-3"
              disabled={searchSettings.enabled === undefined}
              checked={searchSettings.enabled === true}
              onCheckedChange={(isChecked) => {
                handleSearchConfigChange({ enabled: isChecked });
              }}
            />
            <div className="space-y-0.5">
              <Label htmlFor="enabled">启用</Label>
            </div>
          </div>
          <div className="flex flex-col">
            <div className="flex flex-row items-center">
              <Switch
                id="reindex"
                className="mr-3"
                disabled={searchSettings.reindex === undefined}
                checked={searchSettings.reindex === true}
                onCheckedChange={(isChecked) => {
                  handleSearchConfigChange({ reindex: isChecked });
                }}
              />
              <div className="space-y-0.5">
                <Label htmlFor="reindex">启动时重新索引</Label>
              </div>
            </div>
            <div className="mt-3 text-sm text-muted-foreground">
              重新索引将重新处理所有缩略图和描述（如果启用），并在每次启动时应用。{" "}
              <em>不要忘记在重启后禁用该选项！</em>
            </div>
          </div>
          <div className="mt-2 flex flex-col space-y-6">
            <div className="space-y-0.5">
              <div className="text-md">模型尺寸</div>
              <div className="space-y-1 text-sm text-muted-foreground">
                <p>
                  用于语义搜索的模型大小。
                </p>
                <ul className="list-disc pl-5 text-sm">
                  <li>
                    <em>小</em> 模型采用模型的量化版本，该版本占用更少的 RAM，在 CPU 上运行速度更快，而嵌入质量的差异非常小。
                  </li>
                  <li>
                    <em>大</em> 模型使用会采用完整的 Jina 模型，如果适用，会自动在 GPU 上运行。
                  </li>
                </ul>
              </div>
            </div>
            <Select
              value={searchSettings.model_size}
              onValueChange={(value) =>
                handleSearchConfigChange({
                  model_size: value as SearchModelSize,
                })
              }
            >
              <SelectTrigger className="w-20">
                {searchSettings.model_size}
              </SelectTrigger>
              <SelectContent>
                <SelectGroup>
                  {["small", "large"].map((size) => (
                    <SelectItem
                      key={size}
                      className="cursor-pointer"
                      value={size}
                    >
                      {size}
                    </SelectItem>
                  ))}
                </SelectGroup>
              </SelectContent>
            </Select>
          </div>
        </div>
        <Separator className="my-2 flex bg-secondary" />

        <div className="flex w-full flex-row items-center gap-2 pt-2 md:w-[25%]">
          <Button className="flex flex-1" aria-label="Reset" onClick={onCancel}>
            重置
          </Button>
          <Button
            variant="select"
            disabled={!changedValue || isLoading}
            className="flex flex-1"
            aria-label="Save"
            onClick={saveToConfig}
          >
            {isLoading ? (
              <div className="flex flex-row items-center gap-2">
                <ActivityIndicator />
                <span>保存中...</span>
              </div>
            ) : (
              "保存"
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}
