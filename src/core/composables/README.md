# Composables

This directory contains reusable Vue composables for the project.

## useAlertDialog

A composable for programmatically displaying alert dialogs.

### Usage

```typescript
import { useAlertDialog } from '@/composables';

// In your component setup
const alertDialog = useAlertDialog();

// Open a basic dialog
alertDialog.open({
  title: 'Basic Dialog',
  description: 'This is a basic dialog example.',
  confirmText: 'Confirm',
  cancelText: 'Cancel',
  onConfirm: () => {
    console.log('Confirm button clicked');
  },
  onCancel: () => {
    console.log('Cancel button clicked');
  },
});

// Open an alert dialog (only confirm button)
alertDialog.alert(
  'Alert',
  'This is an alert dialog example.',
  () => {
    console.log('Confirm button clicked');
  }
);

// Open a confirm dialog (confirm and cancel buttons)
alertDialog.confirm(
  'Confirmation Required',
  'Are you sure you want to perform this action?',
  () => {
    console.log('Confirm button clicked');
  },
  () => {
    console.log('Cancel button clicked');
  }
);

// Close the dialog programmatically
alertDialog.close();

// Check if the dialog is open
console.log(alertDialog.isOpen.value);
```

### API

The `useAlertDialog` composable returns an object with the following methods:

- `open(options: AlertDialogOptions)`: Open a dialog with custom options
- `close()`: Close the dialog
- `alert(title: string, description?: string, onConfirm?: () => void)`: Open an alert dialog with only a confirm button
- `confirm(title: string, description?: string, onConfirm?: () => void, onCancel?: () => void)`: Open a confirm dialog with confirm and cancel buttons
- `isOpen`: A ref indicating whether the dialog is currently open

### Options

The `open` method accepts an options object with the following properties:

```typescript
interface AlertDialogOptions {
  title?: string;              // Dialog title
  description?: string;        // Dialog description
  confirmText?: string;        // Text for the confirm button (default: "확인")
  cancelText?: string;         // Text for the cancel button (default: "취소")
  onConfirm?: () => void;      // Callback when confirm button is clicked
  onCancel?: () => void;       // Callback when cancel button is clicked
}
```

### Example Component

See `src/examples/AlertDialogExample.vue` for a complete example of using the `useAlertDialog` composable.

## useToast

A composable for easier usage of toast notifications using vue-sonner.

### Usage

```typescript
import { useToast } from '@/composables';

// In your component setup
const toast = useToast();

// Show a success toast
toast.success('Success!', {
  description: 'Operation completed successfully',
});

// Show an error toast
toast.error('Error!', {
  description: 'Something went wrong',
});

// Show an info toast
toast.info('Information', {
  description: 'Here is some information',
});

// Show a warning toast
toast.warning('Warning', {
  description: 'This is a warning message',
});

// Show a loading toast
toast.loading('Loading...', {
  description: 'Please wait',
});

// Show a toast for a promise
const promise = fetchData();
toast.promise(promise, {
  loading: 'Loading data...',
  success: 'Data loaded successfully!',
  error: 'Failed to load data',
});

// Dismiss a toast
const toastId = toast.success('This will be dismissed');
toast.dismiss(toastId);
```

### API

The `useToast` composable returns an object with the following methods:

- `success(message: string, options?: ExternalToast)`: Show a success toast
- `error(message: string, options?: ExternalToast)`: Show an error toast
- `info(message: string, options?: ExternalToast)`: Show an info toast
- `warning(message: string, options?: ExternalToast)`: Show a warning toast
- `loading(message: string, options?: ExternalToast)`: Show a loading toast
- `custom(message: string, options?: ExternalToast)`: Show a custom toast
- `dismiss(id?: string | number)`: Dismiss a toast by ID
- `promise<T>(promise: Promise<T> | (() => Promise<T>), options?: PromiseOptions)`: Show a toast for a promise

### Default Options

All toast methods use these default options which can be overridden:

```typescript
const defaultOptions = {
  duration: 5000,
  position: 'top-center'
};
```

### Example Component

See `src/components/examples/ToastExample.vue` for a complete example of using the `useToast` composable.
