import { Button } from "../ui/button";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "../ui/dialog";

type SetPasswordProps = {
  show: boolean;
  onDelete: () => void;
  onCancel: () => void;
};
export default function DeleteUserDialog({
  show,
  onDelete,
  onCancel,
}: SetPasswordProps) {
  return (
    <Dialog open={show} onOpenChange={onCancel}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>删除用户</DialogTitle>
        </DialogHeader>
        <div>您确定？</div>
        <DialogFooter>
          <Button
            className="flex items-center gap-1"
            aria-label="Confirm delete"
            variant="destructive"
            size="sm"
            onClick={onDelete}
          >
            删除
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
