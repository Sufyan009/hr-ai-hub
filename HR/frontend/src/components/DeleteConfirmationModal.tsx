import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { AlertTriangle } from "lucide-react";

interface DeleteConfirmationModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onConfirm: () => void;
  jobTitle: string;
  isDeleting?: boolean;
}

export const DeleteConfirmationModal = ({ 
  open, 
  onOpenChange, 
  onConfirm, 
  jobTitle,
  isDeleting = false
}: DeleteConfirmationModalProps) => {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px] bg-card border-border">
        <DialogHeader className="space-y-4">
          <div className="flex items-center justify-center w-12 h-12 mx-auto bg-destructive/10 rounded-full">
            <AlertTriangle className="w-6 h-6 text-destructive" />
          </div>
          <DialogTitle className="text-center text-foreground">
            Delete Job Posting
          </DialogTitle>
          <DialogDescription className="text-center text-muted-foreground">
            Are you sure you want to delete the job posting{" "}
            <span className="font-semibold text-foreground">"{jobTitle}"</span>?
            <br />
            <span className="text-destructive font-medium">This action cannot be undone.</span>
          </DialogDescription>
        </DialogHeader>

        <DialogFooter className="gap-2 sm:gap-2">
          <Button 
            type="button" 
            variant="outline" 
            onClick={() => onOpenChange(false)}
            disabled={isDeleting}
            className="border-border hover:bg-accent"
          >
            Cancel
          </Button>
          <Button 
            type="button" 
            variant="destructive"
            onClick={onConfirm}
            disabled={isDeleting}
            className="bg-destructive hover:bg-destructive/90"
          >
            {isDeleting ? 'Deleting...' : 'Delete'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};