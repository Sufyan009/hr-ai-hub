import { useToast } from "@/hooks/use-toast"
import {
  Toast,
  ToastClose,
  ToastDescription,
  ToastProvider,
  ToastTitle,
  ToastViewport,
} from "@/components/ui/toast"
import { useEffect } from "react";

export function Toaster() {
  const { toasts } = useToast()

  // Update ARIA live region for screen readers
  useEffect(() => {
    if (toasts.length > 0) {
      const toast = toasts[0];
      const liveRegion = document.getElementById("aria-live-toast");
      if (liveRegion) {
        liveRegion.textContent = `${toast.title ? (typeof toast.title === 'string' ? toast.title : '') : ''} ${toast.description ? (typeof toast.description === 'string' ? toast.description : '') : ''}`.trim();
      }
    }
  }, [toasts]);

  return (
    <ToastProvider>
      {toasts.map(function ({ id, title, description, action, ...props }) {
        return (
          <Toast key={id} {...props}>
            <div className="grid gap-1">
              {title && <ToastTitle>{title}</ToastTitle>}
              {description && (
                <ToastDescription>{description}</ToastDescription>
              )}
            </div>
            {action}
            <ToastClose />
          </Toast>
        )
      })}
      <ToastViewport />
    </ToastProvider>
  )
}
