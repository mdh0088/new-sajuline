import type { ComputedRef, MaybeRef } from 'vue'
export type LayoutKey = "default" | "desktop"
declare module 'nuxt/app' {
  interface PageMeta {
    layout?: MaybeRef<LayoutKey | false> | ComputedRef<LayoutKey | false>
  }
}