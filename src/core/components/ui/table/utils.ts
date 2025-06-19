import type { Updater } from '@tanstack/vue-table'
import type { Ref } from 'vue'

export function valueUpdater<T extends Updater<any>>(updaterOrValue: T, ref: Ref) {
  console.log('valueUpdater called with:', {
    updaterOrValue,
    currentRefValue: ref.value,
    isFunction: typeof updaterOrValue === 'function'
  })

  const newValue = typeof updaterOrValue === 'function'
    ? updaterOrValue(ref.value)
    : updaterOrValue

  console.log('valueUpdater setting new value:', newValue)
  ref.value = newValue
}
