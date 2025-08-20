<template>
  <div class="rich-text-editor">
    <!-- 툴바 -->
    <div class="toolbar border-b border-gray-200 bg-gray-50 p-2 flex flex-wrap gap-1 dark:border-gray-700 dark:bg-gray-800/20">
      <!-- 텍스트 포맷팅 -->
      <div class="flex gap-1 border-r border-gray-200 pr-2 mr-2 dark:border-gray-700">
        <ToolbarButton
          @click="editor?.chain().focus().toggleBold().run()"
          :is-active="editor?.isActive('bold')"
          title="Bold (Ctrl+B)"
        >
          <Bold class="h-4 w-4" />
        </ToolbarButton>
        
        <ToolbarButton
          @click="editor?.chain().focus().toggleItalic().run()"
          :is-active="editor?.isActive('italic')"
          title="Italic (Ctrl+I)"
        >
          <Italic class="h-4 w-4" />
        </ToolbarButton>
        
        <ToolbarButton
          @click="editor?.chain().focus().toggleUnderline().run()"
          :is-active="editor?.isActive('underline')"
          title="Underline (Ctrl+U)"
        >
          <UnderlineIcon class="h-4 w-4" />
        </ToolbarButton>
        
        <ToolbarButton
          @click="editor?.chain().focus().toggleStrike().run()"
          :is-active="editor?.isActive('strike')"
          title="Strike through"
        >
          <Strikethrough class="h-4 w-4" />
        </ToolbarButton>
      </div>

      <!-- 헤딩 -->
      <div class="flex gap-1 border-r border-gray-200 dark:border-gray-700 pr-2 mr-2">
        <ToolbarButton
          @click="editor?.chain().focus().toggleHeading({ level: 1 }).run()"
          :is-active="editor?.isActive('heading', { level: 1 })"
          title="Heading 1"
        >
          H1
        </ToolbarButton>
        
        <ToolbarButton
          @click="editor?.chain().focus().toggleHeading({ level: 2 }).run()"
          :is-active="editor?.isActive('heading', { level: 2 })"
          title="Heading 2"
        >
          H2
        </ToolbarButton>
        
        <ToolbarButton
          @click="editor?.chain().focus().toggleHeading({ level: 3 }).run()"
          :is-active="editor?.isActive('heading', { level: 3 })"
          title="Heading 3"
        >
          H3
        </ToolbarButton>
      </div>

      <!-- 목록 -->
      <div class="flex gap-1 border-r border-gray-200 dark:border-gray-700 pr-2 mr-2">
        <ToolbarButton
          @click="editor?.chain().focus().toggleBulletList().run()"
          :is-active="editor?.isActive('bulletList')"
          title="Bullet List"
        >
          <List class="h-4 w-4" />
        </ToolbarButton>
        
        <ToolbarButton
          @click="editor?.chain().focus().toggleOrderedList().run()"
          :is-active="editor?.isActive('orderedList')"
          title="Ordered List"
        >
          <ListOrdered class="h-4 w-4" />
        </ToolbarButton>
      </div>

      <!-- 기타 -->
      <div class="flex gap-1 border-r border-gray-200 dark:border-gray-700 pr-2 mr-2">
        <ToolbarButton
          @click="editor?.chain().focus().toggleBlockquote().run()"
          :is-active="editor?.isActive('blockquote')"
          title="Blockquote"
        >
          <Quote class="h-4 w-4" />
        </ToolbarButton>
        
        <ToolbarButton
          @click="editor?.chain().focus().toggleCode().run()"
          :is-active="editor?.isActive('code')"
          title="Code"
        >
          <Code class="h-4 w-4" />
        </ToolbarButton>
        
        <ToolbarButton
          @click="editor?.chain().focus().setHorizontalRule().run()"
          title="Horizontal Rule"
        >
          <Minus class="h-4 w-4" />
        </ToolbarButton>
      </div>

      <!-- 테이블 기능 임시 비활성화 -->
      <!-- <div class="flex gap-1 border-r border-gray-200 dark:border-gray-700 pr-2 mr-2">
        <ToolbarButton
          @click="insertTable"
          title="Insert Table"
        >
          <Table class="h-4 w-4" />
        </ToolbarButton>
      </div> -->

      <!-- 링크 -->
      <div class="flex gap-1">
        <ToolbarButton
          @click="setLink"
          :is-active="editor?.isActive('link')"
          title="Add Link (Ctrl+K)"
        >
          <LinkIcon class="h-4 w-4" />
        </ToolbarButton>
      </div>
    </div>

    <!-- 에디터 영역 -->
    <div class="editor-content">
      <EditorContent 
        :editor="editor" 
        class="min-h-[400px] p-4 prose prose-sm max-w-none focus:outline-none"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch } from 'vue';
import { Editor, EditorContent } from '@tiptap/vue-3';
import StarterKit from '@tiptap/starter-kit';
import Link from '@tiptap/extension-link';
import Underline from '@tiptap/extension-underline';
// 테이블 확장 기능은 임시로 비활성화
// import Table from '@tiptap/extension-table';
// import TableRow from '@tiptap/extension-table-row';
// import TableHeader from '@tiptap/extension-table-header';
// import TableCell from '@tiptap/extension-table-cell';
import TextAlign from '@tiptap/extension-text-align';
import Highlight from '@tiptap/extension-highlight';

import { 
  Bold, 
  Italic, 
  Underline as UnderlineIcon, 
  Strikethrough, 
  List, 
  ListOrdered, 
  Quote, 
  Code, 
  Minus,
  // Table as TableIcon, // 임시 비활성화
  Link as LinkIcon
} from 'lucide-vue-next';

import ToolbarButton from './ToolbarButton.vue';

// Props & Emits
interface Props {
  modelValue: string;
  placeholder?: string;
  disabled?: boolean;
}

interface Emits {
  (e: 'update:modelValue', value: string): void;
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: '내용을 입력하세요...',
  disabled: false,
});

const emit = defineEmits<Emits>();

// Editor instance
const editor = ref<Editor>();

// Editor 초기화
onMounted(() => {
  editor.value = new Editor({
    content: props.modelValue,
    extensions: [
      StarterKit.configure({
        heading: {
          levels: [1, 2, 3, 4, 5, 6],
        },
        // StarterKit의 link와 underline를 비활성화하여 중복 방지
        link: false,
        underline: false,
      }),
      Link.configure({
        openOnClick: false,
        HTMLAttributes: {
          class: 'text-primary underline underline-offset-2',
        },
      }),
      Underline,
      // 테이블 확장 기능은 임시로 비활성화
      // Table.configure({
      //   resizable: true,
      // }),
      // TableRow,
      // TableHeader.extend({
      //   content: 'paragraph*',
      // }),
      // TableCell.extend({
      //   content: 'paragraph*',
      // }),
      TextAlign.configure({
        types: ['heading', 'paragraph'],
      }),
      Highlight.configure({
        multicolor: true,
      }),
    ],
    onUpdate: ({ editor }) => {
      emit('update:modelValue', editor.getHTML());
    },
    editorProps: {
      attributes: {
        class: 'focus:outline-none prose prose-sm max-w-none',
        placeholder: props.placeholder,
      },
    },
    editable: !props.disabled,
  });
});

// Cleanup
onBeforeUnmount(() => {
  editor.value?.destroy();
});

// Props 변경 감지
watch(() => props.modelValue, (newValue) => {
  if (editor.value && editor.value.getHTML() !== newValue) {
    editor.value.commands.setContent(newValue, false);
  }
});

watch(() => props.disabled, (newValue) => {
  editor.value?.setEditable(!newValue);
});

// 테이블 삽입 (임시 비활성화)
// const insertTable = () => {
//   editor.value?.chain().focus().insertTable({ 
//     rows: 3, 
//     cols: 3, 
//     withHeaderRow: true 
//   }).run();
// };

// 링크 설정
const setLink = () => {
  const previousUrl = editor.value?.getAttributes('link').href;
  const url = window.prompt('URL을 입력하세요', previousUrl);

  if (url === null) {
    return;
  }

  if (url === '') {
    editor.value?.chain().focus().extendMarkRange('link').unsetLink().run();
    return;
  }

  editor.value?.chain().focus().extendMarkRange('link').setLink({ href: url }).run();
};
</script>

<style scoped>
.rich-text-editor {
  border: 1px solid #e5e7eb;
  border-radius: 0.375rem;
  background-color: white;
  overflow: hidden;
}

.dark .rich-text-editor {
  border-color: #374151;
  background-color: #111827;
}

.toolbar {
  border-bottom: 1px solid #e5e7eb;
  background-color: #f9fafb;
}

.dark .toolbar {
  border-color: #374151;
  background-color: rgba(31, 41, 55, 0.2);
}

.editor-content {
  background-color: white;
}

.dark .editor-content {
  background-color: #111827;
}

:deep(.ProseMirror) {
  background-color: white;
  color: #111827;
  outline: none;
  padding: 1rem;
  min-height: 400px;
}

.dark :deep(.ProseMirror) {
  background-color: #111827;
  color: #f9fafb;
}

:deep(.ProseMirror p) {
  color: inherit;
  margin: 0.5rem 0;
}

:deep(.ProseMirror h1) {
  font-size: 1.875rem;
  font-weight: 700;
  color: inherit;
  margin: 1.5rem 0 1rem 0;
}

:deep(.ProseMirror h2) {
  font-size: 1.5rem;
  font-weight: 600;
  color: inherit;
  margin: 1.25rem 0 0.75rem 0;
}

:deep(.ProseMirror h3) {
  font-size: 1.25rem;
  font-weight: 600;
  color: inherit;
  margin: 1rem 0 0.5rem 0;
}

:deep(.ProseMirror strong) {
  font-weight: 600;
  color: inherit;
}

:deep(.ProseMirror em) {
  font-style: italic;
  color: inherit;
}

:deep(.ProseMirror code) {
  background-color: #f3f4f6;
  color: #111827;
  padding: 0.125rem 0.25rem;
  border-radius: 0.25rem;
  font-size: 0.875rem;
  font-family: ui-monospace, SFMono-Regular, Consolas, 'Liberation Mono', Menlo, monospace;
}

.dark :deep(.ProseMirror code) {
  background-color: #1f2937;
  color: #f9fafb;
}

:deep(.ProseMirror pre) {
  background-color: #f3f4f6;
  color: #111827;
  padding: 1rem;
  border-radius: 0.375rem;
  margin: 1rem 0;
  overflow-x: auto;
}

.dark :deep(.ProseMirror pre) {
  background-color: #1f2937;
  color: #f9fafb;
}

:deep(.ProseMirror blockquote) {
  border-left: 4px solid #e5e7eb;
  padding-left: 1rem;
  margin: 1rem 0;
  color: #6b7280;
  font-style: italic;
}

.dark :deep(.ProseMirror blockquote) {
  border-color: #374151;
  color: #9ca3af;
}

:deep(.ProseMirror ul) {
  list-style-type: disc;
  padding-left: 1.5rem;
  margin: 0.5rem 0;
}

:deep(.ProseMirror ol) {
  list-style-type: decimal;
  padding-left: 1.5rem;
  margin: 0.5rem 0;
}

:deep(.ProseMirror li) {
  color: inherit;
  margin: 0.25rem 0;
}

:deep(.ProseMirror hr) {
  border-top: 1px solid #e5e7eb;
  margin: 1.5rem 0;
}

.dark :deep(.ProseMirror hr) {
  border-color: #374151;
}

:deep(.ProseMirror table) {
  border-collapse: collapse;
  border: 1px solid #e5e7eb;
  margin: 1rem 0;
  width: 100%;
}

.dark :deep(.ProseMirror table) {
  border-color: #374151;
}

:deep(.ProseMirror td),
:deep(.ProseMirror th) {
  border: 1px solid #e5e7eb;
  padding: 0.75rem;
  text-align: left;
  color: inherit;
}

.dark :deep(.ProseMirror td),
.dark :deep(.ProseMirror th) {
  border-color: #374151;
}

:deep(.ProseMirror th) {
  background-color: #f3f4f6;
  font-weight: 600;
}

.dark :deep(.ProseMirror th) {
  background-color: #1f2937;
}

:deep(.ProseMirror a) {
  color: #2563eb;
  text-decoration: underline;
  text-underline-offset: 2px;
}

.dark :deep(.ProseMirror a) {
  color: #3b82f6;
}

:deep(.ProseMirror .is-empty::before) {
  content: attr(placeholder);
  color: #6b7280;
  pointer-events: none;
  float: left;
  height: 0;
}

.dark :deep(.ProseMirror .is-empty::before) {
  color: #9ca3af;
}
</style>