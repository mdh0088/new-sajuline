import { RuntimeConfig as UserRuntimeConfig, PublicRuntimeConfig as UserPublicRuntimeConfig } from 'nuxt/schema'
  interface SharedRuntimeConfig {
   app: {
      buildId: string,

      baseURL: string,

      buildAssetsDir: string,

      cdnURL: string,
   },

   apiSecret: string,

   proxyTarget: string,

   nitro: {
      envPrefix: string,
   },

   "nuxt-scripts": {
      version: string,
   },

   icon: {
      serverKnownCssClasses: Array<any>,
   },
  }
  interface SharedPublicRuntimeConfig {
   apiBase: string,

   kakaoClientId: string,

   naverClientId: string,

   siteUrl: string,

   sentryDsn: string,

   cdnBase: string,

   "nuxt-scripts": {
      version: any,

      defaultScriptOptions: {
         trigger: string,
      },
   },

   notivue: {
      position: string,

      limit: number,

      enqueue: boolean,

      avoidDuplicates: boolean,

      notifications: {
         global: {
            duration: number,
         },
      },
   },
  }
declare module '@nuxt/schema' {
  interface RuntimeConfig extends UserRuntimeConfig {}
  interface PublicRuntimeConfig extends UserPublicRuntimeConfig {}
}
declare module 'nuxt/schema' {
  interface RuntimeConfig extends SharedRuntimeConfig {}
  interface PublicRuntimeConfig extends SharedPublicRuntimeConfig {}
}
declare module 'vue' {
        interface ComponentCustomProperties {
          $config: UserRuntimeConfig
        }
      }