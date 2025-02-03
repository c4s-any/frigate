import { FaCircleCheck } from "react-icons/fa6";
import { useCallback, useState } from "react";
import axios from "axios";
import { Button, buttonVariants } from "../ui/button";
import { isDesktop } from "react-device-detect";
import { FaCompactDisc } from "react-icons/fa";
import { HiTrash } from "react-icons/hi";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "../ui/alert-dialog";
import useKeyboardListener from "@/hooks/use-keyboard-listener";

type ReviewActionGroupProps = {
  selectedReviews: string[];
  setSelectedReviews: (ids: string[]) => void;
  onExport: (id: string) => void;
  pullLatestData: () => void;
};
export default function ReviewActionGroup({
  selectedReviews,
  setSelectedReviews,
  onExport,
  pullLatestData,
}: ReviewActionGroupProps) {
  const onClearSelected = useCallback(() => {
    setSelectedReviews([]);
  }, [setSelectedReviews]);

  const onMarkAsReviewed = useCallback(async () => {
    await axios.post(`reviews/viewed`, { ids: selectedReviews });
    setSelectedReviews([]);
    pullLatestData();
  }, [selectedReviews, setSelectedReviews, pullLatestData]);

  const onDelete = useCallback(async () => {
    await axios.post(`reviews/delete`, { ids: selectedReviews });
    setSelectedReviews([]);
    pullLatestData();
  }, [selectedReviews, setSelectedReviews, pullLatestData]);

  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [bypassDialog, setBypassDialog] = useState(false);

  useKeyboardListener(["Shift"], (_, modifiers) => {
    setBypassDialog(modifiers.shift);
  });

  const handleDelete = useCallback(() => {
    if (bypassDialog) {
      onDelete();
    } else {
      setDeleteDialogOpen(true);
    }
  }, [bypassDialog, onDelete]);

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
            您确定要删除与所选审核项相关的所有录像视频吗？
            <br />
            <br />
            以后按住 <em>Shift</em> 键可绕过此对话框。
          </AlertDialogDescription>
          <AlertDialogFooter>
            <AlertDialogCancel>取消</AlertDialogCancel>
            <AlertDialogAction
              className={buttonVariants({ variant: "destructive" })}
              onClick={onDelete}
            >
              删除
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      <div className="absolute inset-x-2 inset-y-0 flex items-center justify-between gap-2 bg-background py-2 md:left-auto">
        <div className="mx-1 flex items-center justify-center text-sm text-muted-foreground">
          <div className="p-1">{`${selectedReviews.length} selected`}</div>
          <div className="p-1">{"|"}</div>
          <div
            className="cursor-pointer p-2 text-primary hover:rounded-lg hover:bg-secondary"
            onClick={onClearSelected}
          >
            未选
          </div>
        </div>
        <div className="flex items-center gap-1 md:gap-2">
          {selectedReviews.length == 1 && (
            <Button
              className="flex items-center gap-2 p-2"
              aria-label="Export"
              size="sm"
              onClick={() => {
                onExport(selectedReviews[0]);
                onClearSelected();
              }}
            >
              <FaCompactDisc className="text-secondary-foreground" />
              {isDesktop && <div className="text-primary">导出</div>}
            </Button>
          )}
          <Button
            className="flex items-center gap-2 p-2"
            aria-label="Mark as reviewed"
            size="sm"
            onClick={onMarkAsReviewed}
          >
            <FaCircleCheck className="text-secondary-foreground" />
            {isDesktop && <div className="text-primary">标记为已审核</div>}
          </Button>
          <Button
            className="flex items-center gap-2 p-2"
            aria-label="Delete"
            size="sm"
            onClick={handleDelete}
          >
            <HiTrash className="text-secondary-foreground" />
            {isDesktop && (
              <div className="text-primary">
                {bypassDialog ? "立即删除" : "删除"}
              </div>
            )}
          </Button>
        </div>
      </div>
    </>
  );
}
