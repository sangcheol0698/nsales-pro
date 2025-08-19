import { ref, readonly, computed } from 'vue';
import { container } from 'tsyringe';
import { Users } from 'lucide-vue-next';
import DepartmentRepository from '@/core/repositories/DepartmentRepository.ts';
import Department from '@/core/entities/Department.ts';

// Global state
const departments = ref<Department[]>([]);
const loading = ref(false);
const error = ref<string | null>(null);
const lastFetched = ref<number | null>(null);

// Cache timeout (5 minutes)
const CACHE_TIMEOUT = 5 * 60 * 1000;

export function useDepartments() {
  const repository = container.resolve(DepartmentRepository);

  const fetchDepartments = async (forceRefresh = false) => {
    // Check if we have cached data and it's still valid
    if (!forceRefresh && departments.value.length > 0 && lastFetched.value) {
      const now = Date.now();
      if (now - lastFetched.value < CACHE_TIMEOUT) {
        return departments.value;
      }
    }

    loading.value = true;
    error.value = null;

    try {
      const response = await repository.getDepartments();
      departments.value = response;
      lastFetched.value = Date.now();
      return response;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch departments';
      console.error('Error fetching departments:', err);
      // Don't clear existing data on error, just return what we have
      return departments.value;
    } finally {
      loading.value = false;
    }
  };

  const clearCache = () => {
    departments.value = [];
    lastFetched.value = null;
    error.value = null;
  };

  // Generate options for select components
  const departmentOptions = computed(() => 
    departments.value.map(dept => ({
      label: dept.name,
      value: dept.id, // 숫자 타입 유지
      icon: Users, // You may want to import this or make it configurable
    }))
  );

  return {
    departments: readonly(departments),
    loading: readonly(loading),
    error: readonly(error),
    departmentOptions,
    fetchDepartments,
    clearCache,
  };
}