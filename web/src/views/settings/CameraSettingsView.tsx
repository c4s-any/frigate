import Heading from "@/components/ui/heading";
import { useCallback, useContext, useEffect, useMemo, useState } from "react";
import { Toaster } from "sonner";
import { toast } from "sonner";
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { Separator } from "../../components/ui/separator";
import { Button } from "../../components/ui/button";
import useSWR from "swr";
import { FrigateConfig } from "@/types/frigateConfig";
import { Checkbox } from "@/components/ui/checkbox";
import ActivityIndicator from "@/components/indicators/activity-indicator";
import { StatusBarMessagesContext } from "@/context/statusbar-provider";
import axios from "axios";
import { Link } from "react-router-dom";
import { LuExternalLink } from "react-icons/lu";
import { capitalizeFirstLetter } from "@/utils/stringUtil";
import { MdCircle } from "react-icons/md";
import { cn } from "@/lib/utils";

type CameraSettingsViewProps = {
  selectedCamera: string;
  setUnsavedChanges: React.Dispatch<React.SetStateAction<boolean>>;
};

type CameraReviewSettingsValueType = {
  alerts_zones: string[];
  detections_zones: string[];
};

export default function CameraSettingsView({
  selectedCamera,
  setUnsavedChanges,
}: CameraSettingsViewProps) {
  const { data: config, mutate: updateConfig } =
    useSWR<FrigateConfig>("config");

  const cameraConfig = useMemo(() => {
    if (config && selectedCamera) {
      return config.cameras[selectedCamera];
    }
  }, [config, selectedCamera]);

  const [changedValue, setChangedValue] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [selectDetections, setSelectDetections] = useState(false);

  const { addMessage, removeMessage } = useContext(StatusBarMessagesContext)!;

  // zones and labels

  const zones = useMemo(() => {
    if (cameraConfig) {
      return Object.entries(cameraConfig.zones).map(([name, zoneData]) => ({
        camera: cameraConfig.name,
        name,
        objects: zoneData.objects,
        color: zoneData.color,
      }));
    }
  }, [cameraConfig]);

  const alertsLabels = useMemo(() => {
    return cameraConfig?.review.alerts.labels
      ? cameraConfig.review.alerts.labels
          .map((label) => label.replaceAll("_", " "))
          .join(", ")
      : "";
  }, [cameraConfig]);

  const detectionsLabels = useMemo(() => {
    return cameraConfig?.review.detections.labels
      ? cameraConfig.review.detections.labels
          .map((label) => label.replaceAll("_", " "))
          .join(", ")
      : "";
  }, [cameraConfig]);

  // form

  const formSchema = z.object({
    alerts_zones: z.array(z.string()),
    detections_zones: z.array(z.string()),
  });

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    mode: "onChange",
    defaultValues: {
      alerts_zones: cameraConfig?.review.alerts.required_zones || [],
      detections_zones: cameraConfig?.review.detections.required_zones || [],
    },
  });

  const watchedAlertsZones = form.watch("alerts_zones");
  const watchedDetectionsZones = form.watch("detections_zones");

  const handleCheckedChange = useCallback(
    (isChecked: boolean) => {
      if (!isChecked) {
        form.reset({
          alerts_zones: watchedAlertsZones,
          detections_zones: [],
        });
      }
      setChangedValue(true);
      setSelectDetections(isChecked as boolean);
    },
    // we know that these deps are correct
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [watchedAlertsZones],
  );

  const saveToConfig = useCallback(
    async (
      { alerts_zones, detections_zones }: CameraReviewSettingsValueType, // values submitted via the form
    ) => {
      const createQuery = (zones: string[], type: "alerts" | "detections") =>
        zones.length
          ? zones
              .map(
                (zone) =>
                  `&cameras.${selectedCamera}.review.${type}.required_zones=${zone}`,
              )
              .join("")
          : cameraConfig?.review[type]?.required_zones &&
              cameraConfig?.review[type]?.required_zones.length > 0
            ? `&cameras.${selectedCamera}.review.${type}.required_zones`
            : "";

      const alertQueries = createQuery(alerts_zones, "alerts");
      const detectionQueries = createQuery(detections_zones, "detections");

      axios
        .put(`config/set?${alertQueries}${detectionQueries}`, {
          requires_restart: 0,
        })
        .then((res) => {
          if (res.status === 200) {
            toast.success(
              `审核分类配置已保存。重启 Frigate 以应用更改。`,
              {
                position: "top-center",
              },
            );
            updateConfig();
          } else {
            toast.error(`无法保存配置更改：${res.statusText}`, {
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
    },
    [updateConfig, setIsLoading, selectedCamera, cameraConfig],
  );

  const onCancel = useCallback(() => {
    if (!cameraConfig) {
      return;
    }

    setChangedValue(false);
    setUnsavedChanges(false);
    removeMessage(
      "camera_settings",
      `review_classification_settings_${selectedCamera}`,
    );
    form.reset({
      alerts_zones: cameraConfig?.review.alerts.required_zones ?? [],
      detections_zones: cameraConfig?.review.detections.required_zones || [],
    });
    setSelectDetections(
      !!cameraConfig?.review.detections.required_zones?.length,
    );
    // we know that these deps are correct
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [removeMessage, selectedCamera, setUnsavedChanges, cameraConfig]);

  useEffect(() => {
    onCancel();
    // we know that these deps are correct
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedCamera]);

  useEffect(() => {
    if (changedValue) {
      addMessage(
        "camera_settings",
        `Unsaved review classification settings for ${capitalizeFirstLetter(selectedCamera)}`,
        undefined,
        `review_classification_settings_${selectedCamera}`,
      );
    } else {
      removeMessage(
        "camera_settings",
        `review_classification_settings_${selectedCamera}`,
      );
    }
    // we know that these deps are correct
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [changedValue, selectedCamera]);

  function onSubmit(values: z.infer<typeof formSchema>) {
    setIsLoading(true);

    saveToConfig(values as CameraReviewSettingsValueType);
  }

  useEffect(() => {
    document.title = "摄像机设置 - Frigate";
  }, []);

  if (!cameraConfig && !selectedCamera) {
    return <ActivityIndicator />;
  }

  return (
    <>
      <div className="flex size-full flex-col md:flex-row">
        <Toaster position="top-center" closeButton={true} />
        <div className="scrollbar-container order-last mb-10 mt-2 flex h-full w-full flex-col overflow-y-auto rounded-lg border-[1px] border-secondary-foreground bg-background_alt p-2 md:order-none md:mb-0 md:mr-2 md:mt-0">
          <Heading as="h3" className="my-2">
            摄像机设置
          </Heading>

          <Separator className="my-2 flex bg-secondary" />

          <Heading as="h4" className="my-2">
            审核分类
          </Heading>

          <div className="max-w-6xl">
            <div className="mb-5 mt-2 flex max-w-5xl flex-col gap-2 text-sm text-primary-variant">
              <p>
                Frigate 将审核项分为 "警报 "和 "检测 "两类。默认情况下，全部<em>火</em>和<em>枪</em>都被视为警报。您可以通过为审核项配置所需的区域来细化审核项的分类。
              </p>
              <div className="flex items-center text-primary">
                <Link
                  to="https://c4s.tech/docs/Frigate/configuration/review"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline"
                >
                  阅读文档{" "}
                  <LuExternalLink className="ml-2 inline-flex size-3" />
                </Link>
              </div>
            </div>
          </div>

          <Form {...form}>
            <form
              onSubmit={form.handleSubmit(onSubmit)}
              className="mt-2 space-y-6"
            >
              <div
                className={cn(
                  "w-full max-w-5xl space-y-0",
                  zones &&
                    zones?.length > 0 &&
                    "grid items-start gap-5 md:grid-cols-2",
                )}
              >
                <FormField
                  control={form.control}
                  name="alerts_zones"
                  render={() => (
                    <FormItem>
                      {zones && zones?.length > 0 ? (
                        <>
                          <div className="mb-2">
                            <FormLabel className="flex flex-row items-center text-base">
                              Alerts{" "}
                              <MdCircle className="ml-3 size-2 text-severity_alert" />
                            </FormLabel>
                            <FormDescription>
                              Select zones for Alerts
                            </FormDescription>
                          </div>
                          <div className="max-w-md rounded-lg bg-secondary p-4 md:max-w-full">
                            {zones?.map((zone) => (
                              <FormField
                                key={zone.name}
                                control={form.control}
                                name="alerts_zones"
                                render={({ field }) => {
                                  return (
                                    <FormItem
                                      key={zone.name}
                                      className="mb-3 flex flex-row items-center space-x-3 space-y-0 last:mb-0"
                                    >
                                      <FormControl>
                                        <Checkbox
                                          className="size-5 text-white accent-white data-[state=checked]:bg-selected data-[state=checked]:text-white"
                                          checked={field.value?.includes(
                                            zone.name,
                                          )}
                                          onCheckedChange={(checked) => {
                                            setChangedValue(true);
                                            return checked
                                              ? field.onChange([
                                                  ...field.value,
                                                  zone.name,
                                                ])
                                              : field.onChange(
                                                  field.value?.filter(
                                                    (value) =>
                                                      value !== zone.name,
                                                  ),
                                                );
                                          }}
                                        />
                                      </FormControl>
                                      <FormLabel className="font-normal capitalize">
                                        {zone.name.replaceAll("_", " ")}
                                      </FormLabel>
                                    </FormItem>
                                  );
                                }}
                              />
                            ))}
                          </div>
                        </>
                      ) : (
                        <div className="font-normal text-destructive">
                          未为该摄像机定义任何防区。
                        </div>
                      )}
                      <FormMessage />
                      <div className="text-sm">
                        全部 {alertsLabels} 目标
                        {watchedAlertsZones && watchedAlertsZones.length > 0
                          ? ` detected in ${watchedAlertsZones.map((zone) => capitalizeFirstLetter(zone).replaceAll("_", " ")).join(", ")}`
                          : ""}{" "}
                        在{" "}
                        {capitalizeFirstLetter(
                          cameraConfig?.name ?? "",
                        ).replaceAll("_", " ")}{" "}
                        将显示为警报。
                      </div>
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="detections_zones"
                  render={() => (
                    <FormItem>
                      {zones && zones?.length > 0 && (
                        <>
                          <div className="mb-2">
                            <FormLabel className="flex flex-row items-center text-base">
                              Detections{" "}
                              <MdCircle className="ml-3 size-2 text-severity_detection" />
                            </FormLabel>
                            {selectDetections && (
                              <FormDescription>
                                Select zones for Detections
                              </FormDescription>
                            )}
                          </div>

                          {selectDetections && (
                            <div className="max-w-md rounded-lg bg-secondary p-4 md:max-w-full">
                              {zones?.map((zone) => (
                                <FormField
                                  key={zone.name}
                                  control={form.control}
                                  name="detections_zones"
                                  render={({ field }) => {
                                    return (
                                      <FormItem
                                        key={zone.name}
                                        className="mb-3 flex flex-row items-center space-x-3 space-y-0 last:mb-0"
                                      >
                                        <FormControl>
                                          <Checkbox
                                            className="size-5 text-white accent-white data-[state=checked]:bg-selected data-[state=checked]:text-white"
                                            checked={field.value?.includes(
                                              zone.name,
                                            )}
                                            onCheckedChange={(checked) => {
                                              return checked
                                                ? field.onChange([
                                                    ...field.value,
                                                    zone.name,
                                                  ])
                                                : field.onChange(
                                                    field.value?.filter(
                                                      (value) =>
                                                        value !== zone.name,
                                                    ),
                                                  );
                                            }}
                                          />
                                        </FormControl>
                                        <FormLabel className="font-normal capitalize">
                                          {zone.name.replaceAll("_", " ")}
                                        </FormLabel>
                                      </FormItem>
                                    );
                                  }}
                                />
                              ))}
                            </div>
                          )}
                          <FormMessage />

                          <div className="mb-0 flex flex-row items-center gap-2">
                            <Checkbox
                              id="select-detections"
                              className="size-5 text-white accent-white data-[state=checked]:bg-selected data-[state=checked]:text-white"
                              checked={selectDetections}
                              onCheckedChange={handleCheckedChange}
                            />
                            <div className="grid gap-1.5 leading-none">
                              <label
                                htmlFor="select-detections"
                                className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                              >
                                将检测限制在特定防区
                              </label>
                            </div>
                          </div>
                        </>
                      )}

                      <div className="text-sm">
                        全部 {detectionsLabels} 目标{" "}
                        <em>未被分类为警报</em>{" "}
                        {watchedDetectionsZones &&
                        watchedDetectionsZones.length > 0
                          ? ` that are detected in ${watchedDetectionsZones.map((zone) => capitalizeFirstLetter(zone).replaceAll("_", " ")).join(", ")}`
                          : ""}{" "}
                        在{" "}
                        {capitalizeFirstLetter(
                          cameraConfig?.name ?? "",
                        ).replaceAll("_", " ")}{" "}
                        将会显示为检测
                        {(!selectDetections ||
                          (watchedDetectionsZones &&
                            watchedDetectionsZones.length === 0)) &&
                          "，不论防区"}
                        .
                      </div>
                    </FormItem>
                  )}
                />
              </div>
              <Separator className="my-2 flex bg-secondary" />

              <div className="flex w-full flex-row items-center gap-2 pt-2 md:w-[25%]">
                <Button
                  className="flex flex-1"
                  aria-label="Cancel"
                  onClick={onCancel}
                  type="button"
                >
                  取消
                </Button>
                <Button
                  variant="select"
                  disabled={isLoading}
                  className="flex flex-1"
                  aria-label="Save"
                  type="submit"
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
            </form>
          </Form>
        </div>
      </div>
    </>
  );
}
