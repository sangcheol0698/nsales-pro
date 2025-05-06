# Composables

This directory contains reusable Vue composables for the project.

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
