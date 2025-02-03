import { useState, ReactNode } from "react";
import { SearchResult } from "@/types/search";
import { FrigateConfig } from "@/types/frigateConfig";
import { baseUrl } from "@/api/baseUrl";
import { toast } from "sonner";
import axios from "axios";
import { LuCamera, LuDownload, LuMoreVertical, LuTrash2 } from "react-icons/lu";
import { FaArrowsRotate } from "react-icons/fa6";
import { MdImageSearch } from "react-icons/md";
import FrigatePlusIcon from "@/components/icons/FrigatePlusIcon";
import { isMobileOnly } from "react-device-detect";
import { buttonVariants } from "@/components/ui/button";
import {
  ContextMenu,
  ContextMenuContent,
  ContextMenuItem,
  ContextMenuTrigger,
} from "@/components/ui/context-menu";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { FrigatePlusDialog } from "@/components/overlay/dialog/FrigatePlusDialog";
import useSWR from "swr";
import { Event } from "@/types/event";

type SearchResultActionsProps = {
  searchResult: SearchResult;
  findSimilar: () => void;
  refreshResults: () => void;
  showObjectLifecycle: () => void;
  isContextMenu?: boolean;
  children?: ReactNode;
};

export default function SearchResultActions({
  searchResult,
  findSimilar,
  refreshResults,
  showObjectLifecycle,
  isContextMenu = false,
  children,
}: SearchResultActionsProps) {
  const { data: config } = useSWR<FrigateConfig>("config");

  const [showFrigatePlus, setShowFrigatePlus] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);

  const handleDelete = () => {
    axios
      .delete(`events/${searchResult.id}`)
      .then((resp) => {
        if (resp.status == 200) {
          toast.success("Tracked object deleted successfully.", {
            position: "top-center",
          });
          refreshResults();
        }
      })
      .catch(() => {
        toast.error("Failed to delete tracked object.", {
          position: "top-center",
        });
      });
  };

  const MenuItem = isContextMenu ? ContextMenuItem : DropdownMenuItem;

  const menuItems = (
    <>
      {searchResult.has_clip && (
        <MenuItem aria-label="Download video">
          <a
            className="flex items-center"
            href={`${baseUrl}api/events/${searchResult.id}/clip.mp4`}
            download={`${searchResult.camera}_${searchResult.label}.mp4`}
          >
            <LuDownload className="mr-2 size-4" />
            <span>下载视频</span>
          </a>
        </MenuItem>
      )}
      {searchResult.has_snapshot && (
        <MenuItem aria-label="Download snapshot">
          <a
            className="flex items-center"
            href={`${baseUrl}api/events/${searchResult.id}/snapshot.jpg`}
            download={`${searchResult.camera}_${searchResult.label}.jpg`}
          >
            <LuCamera className="mr-2 size-4" />
            <span>下载抓拍</span>
          </a>
        </MenuItem>
      )}
      <MenuItem
        aria-label="Show the object lifecycle"
        onClick={showObjectLifecycle}
      >
        <FaArrowsRotate className="mr-2 size-4" />
        <span>查看目标活动周期</span>
      </MenuItem>
      {config?.semantic_search?.enabled && isContextMenu && (
        <MenuItem
          aria-label="Find similar tracked objects"
          onClick={findSimilar}
        >
          <MdImageSearch className="mr-2 size-4" />
          <span>查找相似</span>
        </MenuItem>
      )}
      {isMobileOnly &&
        config?.plus?.enabled &&
        searchResult.has_snapshot &&
        searchResult.end_time &&
        !searchResult.plus_id && (
          <MenuItem
            aria-label="Submit to Frigate Plus"
            onClick={() => setShowFrigatePlus(true)}
          >
            <FrigatePlusIcon className="mr-2 size-4 cursor-pointer text-primary" />
            <span>Submit to Frigate+</span>
          </MenuItem>
        )}
      <MenuItem
        aria-label="Delete this tracked object"
        onClick={() => setDeleteDialogOpen(true)}
      >
        <LuTrash2 className="mr-2 size-4" />
        <span>删除</span>
      </MenuItem>
    </>
  );

  return (
    <>
      <AlertDialog
        open={deleteDialogOpen}
        onOpenChange={() => setDeleteDialogOpen(!deleteDialogOpen)}
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>确认删除</AlertDialogTitle>
          </AlertDialogHeader>
          <AlertDialogDescription>
            您确定要删除此跟踪目标吗？
          </AlertDialogDescription>
          <AlertDialogFooter>
            <AlertDialogCancel>取消</AlertDialogCancel>
            <AlertDialogAction
              className={buttonVariants({ variant: "destructive" })}
              onClick={handleDelete}
            >
              删除
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
      <FrigatePlusDialog
        upload={
          showFrigatePlus ? (searchResult as unknown as Event) : undefined
        }
        onClose={() => setShowFrigatePlus(false)}
        onEventUploaded={() => {
          searchResult.plus_id = "submitted";
        }}
      />

      {isContextMenu ? (
        <ContextMenu>
          <ContextMenuTrigger>{children}</ContextMenuTrigger>
          <ContextMenuContent>{menuItems}</ContextMenuContent>
        </ContextMenu>
      ) : (
        <>
          {config?.semantic_search?.enabled && (
            <Tooltip>
              <TooltipTrigger>
                <MdImageSearch
                  className="size-5 cursor-pointer text-primary-variant hover:text-primary"
                  onClick={findSimilar}
                />
              </TooltipTrigger>
              <TooltipContent>查找相似</TooltipContent>
            </Tooltip>
          )}

          {!isMobileOnly &&
            config?.plus?.enabled &&
            searchResult.has_snapshot &&
            searchResult.end_time &&
            !searchResult.plus_id && (
              <Tooltip>
                <TooltipTrigger>
                  <FrigatePlusIcon
                    className="size-5 cursor-pointer text-primary-variant hover:text-primary"
                    onClick={() => setShowFrigatePlus(true)}
                  />
                </TooltipTrigger>
                <TooltipContent>Submit to Frigate+</TooltipContent>
              </Tooltip>
            )}

          <DropdownMenu>
            <DropdownMenuTrigger>
              <LuMoreVertical className="size-5 cursor-pointer text-primary-variant hover:text-primary" />
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">{menuItems}</DropdownMenuContent>
          </DropdownMenu>
        </>
      )}
    </>
  );
}
