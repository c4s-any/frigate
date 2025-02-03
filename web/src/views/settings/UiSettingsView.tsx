import Heading from "@/components/ui/heading";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { useCallback, useEffect } from "react";
import { Toaster } from "sonner";
import { toast } from "sonner";
import { Separator } from "../../components/ui/separator";
import { Button } from "../../components/ui/button";
import useSWR from "swr";
import { FrigateConfig } from "@/types/frigateConfig";
import { del as delData } from "idb-keyval";
import { usePersistence } from "@/hooks/use-persistence";
import { isSafari } from "react-device-detect";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
} from "../../components/ui/select";

const PLAYBACK_RATE_DEFAULT = isSafari ? [0.5, 1, 2] : [0.5, 1, 2, 4, 8, 16];
const WEEK_STARTS_ON = ["Sunday", "Monday"];

export default function UiSettingsView() {
  const { data: config } = useSWR<FrigateConfig>("config");

  const clearStoredLayouts = useCallback(() => {
    if (!config) {
      return [];
    }

    Object.entries(config.camera_groups).forEach(async (value) => {
      await delData(`${value[0]}-draggable-layout`)
        .then(() => {
          toast.success(`已清除 ${value[0]} 保存的布局`, {
            position: "top-center",
          });
        })
        .catch((error) => {
          toast.error(
            `无法清除保存的布局：${error.response.data.message}`,
            { position: "top-center" },
          );
        });
    });
  }, [config]);

  useEffect(() => {
    document.title = "通用设置 - Frigate";
  }, []);

  // settings

  const [autoLive, setAutoLive] = usePersistence("autoLiveView", true);
  const [playbackRate, setPlaybackRate] = usePersistence("playbackRate", 1);
  const [weekStartsOn, setWeekStartsOn] = usePersistence("weekStartsOn", 0);
  const [alertVideos, setAlertVideos] = usePersistence("alertVideos", true);

  return (
    <>
      <div className="flex size-full flex-col md:flex-row">
        <Toaster position="top-center" closeButton={true} />
        <div className="scrollbar-container order-last mb-10 mt-2 flex h-full w-full flex-col overflow-y-auto rounded-lg border-[1px] border-secondary-foreground bg-background_alt p-2 md:order-none md:mb-0 md:mr-2 md:mt-0">
          <Heading as="h3" className="my-2">
            通用设置
          </Heading>

          <Separator className="my-2 flex bg-secondary" />

          <Heading as="h4" className="my-2">
            实况看板
          </Heading>

          <div className="mt-2 space-y-6">
            <div className="space-y-3">
              <div className="flex flex-row items-center justify-start gap-2">
                <Switch
                  id="auto-live"
                  checked={autoLive}
                  onCheckedChange={setAutoLive}
                />
                <Label className="cursor-pointer" htmlFor="auto-live">
                  自动实况视图
                </Label>
              </div>
              <div className="my-2 text-sm text-muted-foreground">
                <p>
                  检测到活动时自动切换到摄像机的实况视图。禁用此选项会导致实况看板上的静态摄像机图像每分钟只更新一次。
                </p>
              </div>
            </div>
            <div className="space-y-3">
              <div className="flex flex-row items-center justify-start gap-2">
                <Switch
                  id="images-only"
                  checked={alertVideos}
                  onCheckedChange={setAlertVideos}
                />
                <Label className="cursor-pointer" htmlFor="images-only">
                  播放警报视频
                </Label>
              </div>
              <div className="my-2 text-sm text-muted-foreground">
                <p>
                  默认情况下，实况看板上的最新警报会以小循环视频的形式播放。禁用此选项可在此设备/浏览器上只显示最新警报的静态图像。
                </p>
              </div>
            </div>
          </div>

          <div className="my-3 flex w-full flex-col space-y-6">
            <div className="mt-2 space-y-6">
              <div className="space-y-0.5">
                <div className="text-md">保存布局</div>
                <div className="my-2 text-sm text-muted-foreground">
                  <p>
                    可以拖动/调整摄像机组中摄像机的布局。位置会存储在浏览器的本地存储空间中。
                  </p>
                </div>
              </div>
              <Button
                aria-label="Clear all saved layouts"
                onClick={clearStoredLayouts}
              >
                清除所有布局
              </Button>
            </div>

            <Separator className="my-2 flex bg-secondary" />

            <Heading as="h4" className="my-2">
              录像查看器
            </Heading>

            <div className="mt-2 space-y-6">
              <div className="space-y-0.5">
                <div className="text-md">默认回放速率</div>
                <div className="my-2 text-sm text-muted-foreground">
                  <p>录像回放的默认播放速率。</p>
                </div>
              </div>
            </div>
            <Select
              value={playbackRate?.toString()}
              onValueChange={(value) => setPlaybackRate(parseFloat(value))}
            >
              <SelectTrigger className="w-20">
                {`${playbackRate}x`}
              </SelectTrigger>
              <SelectContent>
                <SelectGroup>
                  {PLAYBACK_RATE_DEFAULT.map((rate) => (
                    <SelectItem
                      key={rate}
                      className="cursor-pointer"
                      value={rate.toString()}
                    >
                      {rate}x
                    </SelectItem>
                  ))}
                </SelectGroup>
              </SelectContent>
            </Select>
            <Separator className="my-2 flex bg-secondary" />

            <Heading as="h4" className="my-2">
              日历
            </Heading>

            <div className="mt-2 space-y-6">
              <div className="space-y-0.5">
                <div className="text-md">第一个工作日</div>
                <div className="my-2 text-sm text-muted-foreground">
                  <p>审核日历中各周开始的日期。</p>
                </div>
              </div>
            </div>
            <Select
              value={weekStartsOn?.toString()}
              onValueChange={(value) => setWeekStartsOn(parseInt(value))}
            >
              <SelectTrigger className="w-32">
                {WEEK_STARTS_ON[weekStartsOn ?? 0]}
              </SelectTrigger>
              <SelectContent>
                <SelectGroup>
                  {WEEK_STARTS_ON.map((day, index) => (
                    <SelectItem
                      key={index}
                      className="cursor-pointer"
                      value={index.toString()}
                    >
                      {day}
                    </SelectItem>
                  ))}
                </SelectGroup>
              </SelectContent>
            </Select>
            <Separator className="my-2 flex bg-secondary" />
          </div>
        </div>
      </div>
    </>
  );
}
