import { Alert, AlertTitle, Button } from "@mui/material";

/**
 * Error shown on the page itself. 
 */
export default function InlineError({
    message,
    title,
    onRetry,
}: {
    message: string;
    title?: string;
    onRetry?: () => void;
}) {
    if (!message) {
        return null;
    }

    return (
        <Alert
            severity="error"
            sx={{ mb: 2 }}
            action={
                onRetry && (
                    <Button color="inherit" size="small" onClick={onRetry}>
                        Retry
                    </Button>
                )
            }
        >
            {title && <AlertTitle>{title}</AlertTitle>}
            {message}
        </Alert>
    )
}