import { defineConfig, loadEnv } from 'vite';
import vue from '@vitejs/plugin-vue';
import path from 'path';
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'

export default defineConfig(({ command, mode }) => {
    const env = loadEnv(mode, process.cwd(), '');

    return {
        plugins: [
            vue(),
            AutoImport({
                resolvers: [ElementPlusResolver()],
            }),
            Components({
                resolvers: [ElementPlusResolver()],
            }),
        ],
        server: {
            port: 8088, // 포트 설정
            open: true, // 서버 시작 시 브라우저 자동 열기
            proxy: {
                '/api': {
                    target: env.VITE_APP_API_URL,  // 백엔드 서버 주소
                    changeOrigin: true,
                    secure: false,
                    ws: true
                }
            }
        },
        resolve: {
            alias: [{ find: '@', replacement: path.resolve(__dirname, 'src') }],
            // 확장자 생략 설정
            extensions: ['.mjs', '.js', '.ts', '.jsx', '.tsx', '.json', '.vue']
        },
        optimizeDeps: {
            include: [
                'element-plus/es',
                'element-plus/es/components/base/style/css',
                'element-plus/es/components/row/style/css',
                'element-plus/es/components/col/style/css',
            ],
        },
    };
});
