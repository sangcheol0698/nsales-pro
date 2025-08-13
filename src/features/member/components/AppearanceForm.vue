<template>
  <Form @submit="onSubmit" class="space-y-8">
    <!-- Font Select -->
    <FormItem class="space-y-2">
      <FormLabel>폰트</FormLabel>
      <Select v-model="fontValue" :placeholder="fontValue">
        <FormControl>
          <SelectTrigger class="w-[200px] capitalize">
            <SelectValue>{{ fontValue }}</SelectValue>
          </SelectTrigger>
        </FormControl>
        <SelectContent>
          <SelectItem v-for="f in fontOptions" :key="f" :value="f" class="capitalize">
            {{ f }}
          </SelectItem>
        </SelectContent>
      </Select>
      <FormDescription>대시보드에서 사용할 폰트를 설정합니다.</FormDescription>
      <FormMessage>{{ errors.font }}</FormMessage>
    </FormItem>

    <!-- Theme Radios (Light & Dark) -->
    <FormItem class="space-y-2">
      <FormLabel>테마</FormLabel>
      <FormDescription>대시보드의 테마를 선택합니다.</FormDescription>
      <div class="grid max-w-md grid-cols-2 gap-8 pt-2 items-stretch">
        <!-- Light -->
        <label
          :class="[
            'rounded-md border-2 p-1 cursor-pointer transition-all flex flex-col',
            themeValue === 'light' ? 'border-primary' : 'border-muted',
          ]"
        >
          <input type="radio" value="light" v-model="themeValue" class="sr-only" />
          <div class="border-muted hover:border-accent items-center rounded-md border-2 p-1">
            <div class="space-y-2 rounded-sm bg-[#ecedef] p-2">
              <div class="space-y-2 rounded-md bg-white p-2 shadow-xs">
                <div class="h-2 w-[80px] rounded-lg bg-[#ecedef]" />
                <div class="h-2 w-[100px] rounded-lg bg-[#ecedef]" />
              </div>
              <div class="flex items-center space-x-2 rounded-md bg-white p-2 shadow-xs">
                <div class="h-4 w-4 rounded-full bg-[#ecedef]" />
                <div class="h-2 w-[100px] rounded-lg bg-[#ecedef]" />
              </div>
              <div class="flex items-center space-x-2 rounded-md bg-white p-2 shadow-xs">
                <div class="h-4 w-4 rounded-full bg-[#ecedef]" />
                <div class="h-2 w-[100px] rounded-lg bg-[#ecedef]" />
              </div>
            </div>
          </div>
          <span class="block w-full p-2 text-center font-normal">라이트 모드</span>
        </label>

        <!-- Dark -->
        <label
          :class="[
            'rounded-md border-2 p-1 cursor-pointer transition-all flex flex-col',
            themeValue === 'dark' ? 'border-primary' : 'border-muted',
          ]"
        >
          <input type="radio" value="dark" v-model="themeValue" class="sr-only" />
          <div
            class="border-muted bg-popover hover:bg-accent hover:text-accent-foreground items-center rounded-md border-2 p-1"
          >
            <div class="space-y-2 rounded-sm bg-slate-950 p-2">
              <div class="space-y-2 rounded-md bg-slate-800 p-2 shadow-xs">
                <div class="h-2 w-[80px] rounded-lg bg-slate-400" />
                <div class="h-2 w-[100px] rounded-lg bg-slate-400" />
              </div>
              <div class="flex items-center space-x-2 rounded-md bg-slate-800 p-2 shadow-xs">
                <div class="h-4 w-4 rounded-full bg-slate-400" />
                <div class="h-2 w-[100px] rounded-lg bg-slate-400" />
              </div>
              <div class="flex items-center space-x-2 rounded-md bg-slate-800 p-2 shadow-xs">
                <div class="h-4 w-4 rounded-full bg-slate-400" />
                <div class="h-2 w-[100px] rounded-lg bg-slate-400" />
              </div>
            </div>
          </div>
          <span class="block w-full p-2 text-center font-normal">다크 모드</span>
        </label>
      </div>
      <FormMessage>{{ errors.theme }}</FormMessage>
    </FormItem>

    <!-- Submit Button -->
    <Button type="submit"> 화면 설정 업데이트</Button>
  </Form>
</template>

<script setup lang="ts">
import { onMounted, watch } from 'vue';
import { z } from 'zod';
import { useField, useForm } from 'vee-validate';
import { toTypedSchema } from '@vee-validate/zod';
import { Button } from '@/components/ui/button';
import {
  Form,
  FormControl,
  FormDescription,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

import { type FontName, fonts } from '@/config/fonts';
import { useFont, useTheme } from '@/core/composables';
import type { Theme } from '@/core/composables/useTheme';
import { showSubmittedData } from '@/core/utils/show-submitted-data';

const fontOptions = fonts;

const schema = z.object({
  theme: z.enum(['light', 'dark'], {
    required_error: '테마를 선택해주세요.',
  }),
  font: z.enum(fonts, {
    required_error: '폰트를 선택해주세요.',
    invalid_type_error: '유효하지 않은 폰트입니다.',
  }),
});

const { font, setFont } = useFont();
const { theme, setTheme } = useTheme();

const { handleSubmit, errors, setValues } = useForm({
  validationSchema: toTypedSchema(schema),
  initialValues: {
    font: font.value,
    theme: theme.value,
  },
});

const { value: fontValue } = useField<(typeof fonts)[number]>('font');
const { value: themeValue } = useField<'light' | 'dark'>('theme');

// Watch for changes in theme
// This ensures the form values are always in sync with the actual theme being applied
watch(theme, () => {
  console.log('Theme changed to:', theme.value);
  // Only update if the form value doesn't match the current theme
  if (themeValue.value !== theme.value) {
    console.log('Updating themeValue from', themeValue.value, 'to', theme.value);
    setValues({ theme: theme.value, font: font.value });
  }
});

// Watch for changes in font
// This ensures the form values are always in sync with the actual font being applied
watch(font, () => {
  console.log('Font changed to:', font.value);
  // Only update if the form value doesn't match the current font
  if (fontValue.value !== font.value) {
    console.log('Updating fontValue from', fontValue.value, 'to', font.value);
    setValues({ theme: themeValue.value, font: font.value });
  }
});

// When the component is mounted, update the form values with the theme from localStorage
onMounted(() => {
  console.log('AppearanceForm mounted');
  console.log('Initial font value:', font.value);
  console.log('Initial fontValue:', fontValue.value);
  console.log('Initial theme value:', theme.value);
  console.log('Initial themeValue:', themeValue.value);

  // Check for saved theme in localStorage
  const savedTheme = localStorage.getItem('theme') as Theme | null;
  console.log('Saved theme from localStorage:', savedTheme);

  // Check for saved font in localStorage
  const savedFont = localStorage.getItem('font') as FontName | null;
  console.log('Saved font from localStorage:', savedFont);

  if (
    savedTheme &&
    (savedTheme === 'light' || savedTheme === 'dark') &&
    savedTheme !== themeValue.value
  ) {
    console.log('Setting theme from localStorage:', savedTheme);
    setValues({ theme: savedTheme, font: font.value });
  }

  if (savedFont && fonts.includes(savedFont as FontName) && savedFont !== fontValue.value) {
    console.log('Setting font from localStorage:', savedFont);
    setValues({ theme: themeValue.value, font: savedFont });
  }

  console.log('After initialization - font value:', font.value);
  console.log('After initialization - fontValue:', fontValue.value);
});

const onSubmit = handleSubmit((values) => {
  console.log('Form submitted with values:', values);
  console.log('Current font:', font.value);
  console.log('Current theme:', theme.value);

  if (values.font !== font.value) {
    console.log('Font changed from', font.value, 'to', values.font);
    setFont(values.font);
  } else {
    console.log('Font unchanged:', font.value);
  }

  if (values.theme !== theme.value) {
    console.log('Theme changed from', theme.value, 'to', values.theme);
    setTheme(values.theme);
  } else {
    console.log('Theme unchanged:', theme.value);
  }

  showSubmittedData(values);
});
</script>
