import {
  useEmbeddingsReindexProgress,
  useEventUpdate,
  useModelState,
} from "@/api/ws";
import ActivityIndicator from "@/components/indicators/activity-indicator";
import AnimatedCircularProgressBar from "@/components/ui/circular-progress-bar";
import { useApiFilterArgs } from "@/hooks/use-api-filter";
import { useTimezone } from "@/hooks/use-date-utils";
import { usePersistence } from "@/hooks/use-persistence";
import { FrigateConfig } from "@/types/frigateConfig";
import { SearchFilter, SearchQuery, SearchResult } from "@/types/search";
import { ModelState } from "@/types/ws";
import { formatSecondsToDuration } from "@/utils/dateUtil";
import SearchView from "@/views/search/SearchView";
import { useCallback, useEffect, useMemo, useState } from "react";
import { isMobileOnly } from "react-device-detect";
import { LuCheck, LuExternalLink, LuX } from "react-icons/lu";
import { TbExclamationCircle } from "react-icons/tb";
import { Link } from "react-router-dom";
import { toast } from "sonner";
import useSWR from "swr";
import useSWRInfinite from "swr/infinite";

const API_LIMIT = 25;

export default function Explore() {
  // search field handler

  const { data: config } = useSWR<FrigateConfig>("config", {
    revalidateOnFocus: false,
  });

  // grid

  const [columnCount, setColumnCount] = usePersistence("exploreGridColumns", 4);
  const gridColumns = useMemo(() => {
    if (isMobileOnly) {
      return 2;
    }
    return columnCount ?? 4;
  }, [columnCount]);

  // default layout

  const [defaultView, setDefaultView, defaultViewLoaded] = usePersistence(
    "exploreDefaultView",
    "summary",
  );

  const timezone = useTimezone(config);

  const [search, setSearch] = useState("");

  const [searchFilter, setSearchFilter, searchSearchParams] =
    useApiFilterArgs<SearchFilter>();

  const searchTerm = useMemo(
    () => searchSearchParams?.["query"] || "",
    [searchSearchParams],
  );

  const similaritySearch = useMemo(
    () => searchSearchParams["search_type"] == "similarity",
    [searchSearchParams],
  );

  useEffect(() => {
    if (!searchTerm && !search) {
      return;
    }

    // switch back to normal search when query is entered
    setSearchFilter({
      ...searchFilter,
      search_type:
        similaritySearch && search ? undefined : searchFilter?.search_type,
      event_id: similaritySearch && search ? undefined : searchFilter?.event_id,
      query: search.length > 0 ? search : undefined,
    });
    // only update when search is updated
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [search]);

  const searchQuery: SearchQuery = useMemo(() => {
    // no search parameters
    if (searchSearchParams && Object.keys(searchSearchParams).length === 0) {
      if (defaultView == "grid") {
        return ["events", {}];
      } else {
        return null;
      }
    }

    // parameters, but no search term and not similarity
    if (
      searchSearchParams &&
      Object.keys(searchSearchParams).length !== 0 &&
      !searchTerm &&
      !similaritySearch
    ) {
      return [
        "events",
        {
          cameras: searchSearchParams["cameras"],
          labels: searchSearchParams["labels"],
          sub_labels: searchSearchParams["sub_labels"],
          zones: searchSearchParams["zones"],
          before: searchSearchParams["before"],
          after: searchSearchParams["after"],
          time_range: searchSearchParams["time_range"],
          search_type: searchSearchParams["search_type"],
          min_score: searchSearchParams["min_score"],
          max_score: searchSearchParams["max_score"],
          has_snapshot: searchSearchParams["has_snapshot"],
          has_clip: searchSearchParams["has_clip"],
          limit:
            Object.keys(searchSearchParams).length == 0 ? API_LIMIT : undefined,
          timezone,
          in_progress: 0,
          include_thumbnails: 0,
        },
      ];
    }

    // parameters and search term
    if (!similaritySearch) {
      setSearch(searchTerm);
    }

    return [
      "events/search",
      {
        query: similaritySearch ? undefined : searchTerm,
        cameras: searchSearchParams["cameras"],
        labels: searchSearchParams["labels"],
        sub_labels: searchSearchParams["sub_labels"],
        zones: searchSearchParams["zones"],
        before: searchSearchParams["before"],
        after: searchSearchParams["after"],
        time_range: searchSearchParams["time_range"],
        search_type: searchSearchParams["search_type"],
        min_score: searchSearchParams["min_score"],
        max_score: searchSearchParams["max_score"],
        has_snapshot: searchSearchParams["has_snapshot"],
        has_clip: searchSearchParams["has_clip"],
        event_id: searchSearchParams["event_id"],
        timezone,
        include_thumbnails: 0,
      },
    ];
  }, [searchTerm, searchSearchParams, similaritySearch, timezone, defaultView]);

  // paging

  const getKey = (
    pageIndex: number,
    previousPageData: SearchResult[] | null,
  ): SearchQuery => {
    if (previousPageData && !previousPageData.length) return null; // reached the end
    if (!searchQuery) return null;

    const [url, params] = searchQuery;

    // If it's not the first page, use the last item's start_time as the 'before' parameter
    if (pageIndex > 0 && previousPageData) {
      const lastDate = previousPageData[previousPageData.length - 1].start_time;
      return [
        url,
        { ...params, before: lastDate.toString(), limit: API_LIMIT },
      ];
    }

    // For the first page, use the original params
    return [url, { ...params, limit: API_LIMIT }];
  };

  const { data, size, setSize, isValidating, mutate } = useSWRInfinite<
    SearchResult[]
  >(getKey, {
    revalidateFirstPage: true,
    revalidateOnFocus: true,
    revalidateAll: false,
    onError: (error) => {
      toast.error(
        `Error fetching tracked objects: ${error.response.data.message}`,
        {
          position: "top-center",
        },
      );
      if (error.response.status === 404) {
        // reset all filters if 404
        setSearchFilter({});
      }
    },
  });

  const searchResults = useMemo(
    () => (data ? ([] as SearchResult[]).concat(...data) : []),
    [data],
  );
  const isLoadingInitialData = !data && !isValidating;
  const isLoadingMore =
    isLoadingInitialData ||
    (size > 0 && data && typeof data[size - 1] === "undefined");
  const isEmpty = data?.[0]?.length === 0;
  const isReachingEnd =
    isEmpty || (data && data[data.length - 1]?.length < API_LIMIT);

  const loadMore = useCallback(() => {
    if (!isReachingEnd && !isLoadingMore) {
      if (searchQuery) {
        const [url] = searchQuery;

        // for embeddings, only load 100 results for description and similarity
        if (url === "events/search" && searchResults.length >= 100) {
          return;
        }
      }

      setSize(size + 1);
    }
  }, [isReachingEnd, isLoadingMore, setSize, size, searchResults, searchQuery]);

  // mutation and revalidation

  const eventUpdate = useEventUpdate();

  useEffect(() => {
    if (eventUpdate) {
      mutate();
    }
    // mutate / revalidate when event description updates come in
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [eventUpdate]);

  // embeddings reindex progress

  const { payload: reindexState } = useEmbeddingsReindexProgress();

  const embeddingsReindexing = useMemo(() => {
    if (reindexState) {
      switch (reindexState.status) {
        case "indexing":
          return true;
        case "completed":
          return false;
        default:
          return undefined;
      }
    }
  }, [reindexState]);

  // model states

  const { payload: textModelState } = useModelState(
    "jinaai/jina-clip-v1-text_model_fp16.onnx",
  );
  const { payload: textTokenizerState } = useModelState(
    "jinaai/jina-clip-v1-tokenizer",
  );
  const modelFile =
    config?.semantic_search.model_size === "large"
      ? "jinaai/jina-clip-v1-vision_model_fp16.onnx"
      : "jinaai/jina-clip-v1-vision_model_quantized.onnx";

  const { payload: visionModelState } = useModelState(modelFile);
  const { payload: visionFeatureExtractorState } = useModelState(
    "jinaai/jina-clip-v1-preprocessor_config.json",
  );

  const allModelsLoaded = useMemo(() => {
    return (
      textModelState === "downloaded" &&
      textTokenizerState === "downloaded" &&
      visionModelState === "downloaded" &&
      visionFeatureExtractorState === "downloaded"
    );
  }, [
    textModelState,
    textTokenizerState,
    visionModelState,
    visionFeatureExtractorState,
  ]);

  const renderModelStateIcon = (modelState: ModelState) => {
    if (modelState === "downloading") {
      return <ActivityIndicator className="size-5" />;
    }
    if (modelState === "downloaded") {
      return <LuCheck className="size-5 text-success" />;
    }
    if (modelState === "not_downloaded" || modelState === "error") {
      return <LuX className="size-5 text-danger" />;
    }
    return null;
  };

  if (
    !defaultViewLoaded ||
    (config?.semantic_search.enabled &&
      (!reindexState ||
        !textModelState ||
        !textTokenizerState ||
        !visionModelState ||
        !visionFeatureExtractorState))
  ) {
    return (
      <ActivityIndicator className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2" />
    );
  }

  return (
    <>
      {config?.semantic_search.enabled &&
      (!allModelsLoaded || embeddingsReindexing) ? (
        <div className="absolute inset-0 left-1/2 top-1/2 flex h-96 w-96 -translate-x-1/2 -translate-y-1/2">
          <div className="flex max-w-96 flex-col items-center justify-center space-y-3 rounded-lg bg-background/50 p-5">
            <div className="my-5 flex flex-col items-center gap-2 text-xl">
              <TbExclamationCircle className="mb-3 size-10" />
              <div>搜索不可用</div>
            </div>
            {embeddingsReindexing && allModelsLoaded && (
              <>
                <div className="text-center text-primary-variant">
                  搜索可在被跟踪目标嵌入完成重新索引后使用。
                </div>
                <div className="pt-5 text-center">
                  <AnimatedCircularProgressBar
                    min={0}
                    max={reindexState.total_objects}
                    value={reindexState.processed_objects}
                    gaugePrimaryColor="hsl(var(--selected))"
                    gaugeSecondaryColor="hsl(var(--secondary))"
                  />
                </div>
                <div className="flex w-96 flex-col gap-2 py-5">
                  {reindexState.time_remaining !== null && (
                    <div className="mb-3 flex flex-col items-center justify-center gap-1">
                      <div className="text-primary-variant">
                        {reindexState.time_remaining === -1
                          ? "Starting up..."
                          : "Estimated time remaining:"}
                      </div>
                      {reindexState.time_remaining >= 0 &&
                        (formatSecondsToDuration(reindexState.time_remaining) ||
                          "Finishing shortly")}
                    </div>
                  )}
                  <div className="flex flex-row items-center justify-center gap-3">
                    <span className="text-primary-variant">
                      缩略图已嵌入:
                    </span>
                    {reindexState.thumbnails}
                  </div>
                  <div className="flex flex-row items-center justify-center gap-3">
                    <span className="text-primary-variant">
                      描述已嵌入:
                    </span>
                    {reindexState.descriptions}
                  </div>
                  <div className="flex flex-row items-center justify-center gap-3">
                    <span className="text-primary-variant">
                      被跟踪目标已处理:
                    </span>
                    {reindexState.processed_objects} /{" "}
                    {reindexState.total_objects}
                  </div>
                </div>
              </>
            )}
            {!allModelsLoaded && (
              <>
                <div className="text-center text-primary-variant">
                  Frigate 正在下载支持语义搜索所需的嵌入模型。这可能需要几分钟时间，具体取决于您的网络连接速度。
                </div>
                <div className="flex w-96 flex-col gap-2 py-5">
                  <div className="flex flex-row items-center justify-center gap-2">
                    {renderModelStateIcon(visionModelState)}
                    视觉模式
                  </div>
                  <div className="flex flex-row items-center justify-center gap-2">
                    {renderModelStateIcon(visionFeatureExtractorState)}
                    视觉模型特征提取器
                  </div>
                  <div className="flex flex-row items-center justify-center gap-2">
                    {renderModelStateIcon(textModelState)}
                    文本模式
                  </div>
                  <div className="flex flex-row items-center justify-center gap-2">
                    {renderModelStateIcon(textTokenizerState)}
                    文本标记器
                  </div>
                </div>
                {(textModelState === "error" ||
                  textTokenizerState === "error" ||
                  visionModelState === "error" ||
                  visionFeatureExtractorState === "error") && (
                  <div className="my-3 max-w-96 text-center text-danger">
                    发生错误。检查 Frigate 日志。
                  </div>
                )}
                <div className="text-center text-primary-variant">
                  下载模型后，您可能需要重新索引被跟踪目标的嵌入。
                </div>
                <div className="flex items-center text-primary-variant">
                  <Link
                    to="https://c4s.tech/docs/Frigate/configuration/semantic_search"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline"
                  >
                    阅读文档 {" "}
                    <LuExternalLink className="ml-2 inline-flex size-3" />
                  </Link>
                </div>
              </>
            )}
          </div>
        </div>
      ) : (
        <SearchView
          search={search}
          searchTerm={searchTerm}
          searchFilter={searchFilter}
          searchResults={searchResults}
          isLoading={(isLoadingInitialData || isLoadingMore) ?? true}
          hasMore={!isReachingEnd}
          columns={gridColumns}
          defaultView={defaultView}
          setSearch={setSearch}
          setSimilaritySearch={(search) => {
            setSearchFilter({
              ...searchFilter,
              search_type: ["similarity"],
              event_id: search.id,
            });
          }}
          setSearchFilter={setSearchFilter}
          onUpdateFilter={setSearchFilter}
          setColumns={setColumnCount}
          setDefaultView={setDefaultView}
          loadMore={loadMore}
          refresh={mutate}
        />
      )}
    </>
  );
}
