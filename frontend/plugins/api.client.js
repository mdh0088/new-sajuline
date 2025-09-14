"use strict";
var __assign = (this && this.__assign) || function () {
    __assign = Object.assign || function(t) {
        for (var s, i = 1, n = arguments.length; i < n; i++) {
            s = arguments[i];
            for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p))
                t[p] = s[p];
        }
        return t;
    };
    return __assign.apply(this, arguments);
};
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __generator = (this && this.__generator) || function (thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g = Object.create((typeof Iterator === "function" ? Iterator : Object).prototype);
    return g.next = verb(0), g["throw"] = verb(1), g["return"] = verb(2), typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (g && (g = 0, op[0] && (_ = 0)), _) try {
            if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [op[0] & 2, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
};
Object.defineProperty(exports, "__esModule", { value: true });
/**
 * API 클라이언트 플러그인 (HttpOnly 쿠키 환경)
 * - 전역 $fetch 인스턴스 설정
 * - HttpOnly 쿠키 자동 전송 처리
 * - 요청/응답 인터셉터 구성
 * - 에러 핸들링
 */
var app_1 = require("nuxt/app");
var useNotify_1 = require("~/composables/utils/useNotify");
exports.default = (0, app_1.defineNuxtPlugin)(function () {
    var _a;
    var config = (0, app_1.useRuntimeConfig)();
    var apiBase = ((_a = config.public.apiBase) !== null && _a !== void 0 ? _a : '/api');
    var notifyError = (0, useNotify_1.useNotify)().notifyError;
    // 동시성 제어: 간단한 Promise 공유
    var refreshPromise = null;
    // refresh token 요청 함수 (중복 요청 방지)
    var refreshToken = function () { return __awaiter(void 0, void 0, void 0, function () {
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    if (!refreshPromise) return [3 /*break*/, 2];
                    return [4 /*yield*/, refreshPromise];
                case 1: return [2 /*return*/, _a.sent()];
                case 2:
                    // 새로운 refresh 시작
                    refreshPromise = $fetch('/api/v1/auth/refresh', {
                        baseURL: apiBase,
                        method: 'POST',
                        credentials: 'include',
                        body: {}
                    }).finally(function () {
                        refreshPromise = null; // 완료 후 초기화
                    });
                    return [4 /*yield*/, refreshPromise];
                case 3: return [2 /*return*/, _a.sent()];
            }
        });
    }); };
    // 커스텀 $fetch 인스턴스 생성 (HttpOnly 쿠키 환경)
    var api = $fetch.create({
        baseURL: apiBase,
        credentials: 'include', // HttpOnly 쿠키 자동 전송 (중요!)
        // 요청 전 인터셉터
        onRequest: function (_a) {
            return __awaiter(this, arguments, void 0, function (_b) {
                var headers, csrfMeta, token;
                var request = _b.request, options = _b.options;
                return __generator(this, function (_c) {
                    headers = new Headers(options.headers);
                    headers.set('Content-Type', 'application/json');
                    headers.set('Accept', 'application/json');
                    headers.set('X-Requested-With', 'XMLHttpRequest');
                    // CSRF 토큰 처리 (서버에서 제공하는 경우)
                    if (process.client) {
                        csrfMeta = document.querySelector('meta[name="csrf-token"]');
                        token = csrfMeta === null || csrfMeta === void 0 ? void 0 : csrfMeta.getAttribute('content');
                        if (token) {
                            headers.set('X-CSRF-Token', token);
                        }
                    }
                    options.headers = headers;
                    // 요청 로깅 (개발 환경)
                    if (process.dev) {
                        console.log('🚀 API Request:', {
                            url: request,
                            method: options.method || 'GET',
                            headers: options.headers,
                            body: options.body
                        });
                    }
                    return [2 /*return*/];
                });
            });
        },
        // 응답 성공 인터셉터
        onResponse: function (_a) {
            var response = _a.response;
            // 응답 로깅 (개발 환경)
            if (process.dev) {
                console.log('✅ API Response:', {
                    status: response.status,
                    url: response.url,
                    data: response._data
                });
            }
            // 새로운 CSRF 토큰 업데이트 (헤더에서 제공하는 경우)
            if (process.client) {
                var token = response.headers.get('x-csrf-token');
                if (token) {
                    var csrfMeta = document.querySelector('meta[name="csrf-token"]');
                    if (csrfMeta) {
                        csrfMeta.setAttribute('content', token);
                    }
                }
            }
        },
        // 응답 에러 인터셉터
        onResponseError: function (_a) {
            return __awaiter(this, arguments, void 0, function (_b) {
                var isLoginRequest, errorData_1, errorMessage_1, _1, errorData, errorMessage, errorData, errorMessage;
                var _c, _d;
                var response = _b.response, request = _b.request, options = _b.options;
                return __generator(this, function (_e) {
                    switch (_e.label) {
                        case 0:
                            // 에러 로깅
                            console.error('❌ API Error:', {
                                status: response.status,
                                url: request,
                                data: response._data,
                                timestamp: new Date().toISOString()
                            });
                            if (!(response.status === 401)) return [3 /*break*/, 5];
                            isLoginRequest = request.toString().includes('/login');
                            // 로그인 API 호출인 경우 토큰 갱신 시도하지 않고 바로 에러 메시지 반환
                            if (isLoginRequest) {
                                errorData_1 = response._data;
                                errorMessage_1 = (errorData_1 === null || errorData_1 === void 0 ? void 0 : errorData_1.message) || ((_c = errorData_1 === null || errorData_1 === void 0 ? void 0 : errorData_1.error) === null || _c === void 0 ? void 0 : _c.message) || '아이디 또는 비밀번호가 올바르지 않습니다.';
                                throw (0, app_1.createError)({
                                    statusCode: response.status,
                                    statusMessage: errorMessage_1,
                                    data: errorData_1
                                });
                            }
                            if (!!options._retry) return [3 /*break*/, 4];
                            _e.label = 1;
                        case 1:
                            _e.trys.push([1, 3, , 4]);
                            return [4 /*yield*/, refreshToken()
                                // @ts-expect-error: 내부 재시도 플래그
                            ];
                        case 2:
                            _e.sent();
                            // @ts-expect-error: 내부 재시도 플래그
                            return [2 /*return*/, api(request, __assign(__assign({}, options), { _retry: true }))];
                        case 3:
                            _1 = _e.sent();
                            return [3 /*break*/, 4];
                        case 4:
                            errorData = response._data;
                            errorMessage = (errorData === null || errorData === void 0 ? void 0 : errorData.message) || ((_d = errorData === null || errorData === void 0 ? void 0 : errorData.error) === null || _d === void 0 ? void 0 : _d.message) || '인증이 필요합니다.';
                            throw (0, app_1.createError)({
                                statusCode: response.status,
                                statusMessage: errorMessage,
                                data: errorData
                            });
                        case 5:
                            // 권한 에러 (403)
                            if (response.status === 403) {
                                throw (0, app_1.createError)({
                                    statusCode: 403,
                                    statusMessage: '접근 권한이 없습니다.'
                                });
                            }
                            // 서버 에러 (5xx)
                            if (response.status >= 500) {
                                throw (0, app_1.createError)({
                                    statusCode: response.status,
                                    statusMessage: '서버 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.'
                                });
                            }
                            // 클라이언트 에러 (4xx)
                            if (response.status >= 400) {
                                errorData = response._data;
                                errorMessage = (errorData === null || errorData === void 0 ? void 0 : errorData.message) || (errorData === null || errorData === void 0 ? void 0 : errorData.detail) || '요청 처리 중 오류가 발생했습니다.';
                                throw (0, app_1.createError)({
                                    statusCode: response.status,
                                    statusMessage: errorMessage,
                                    data: errorData
                                });
                            }
                            // 기타 에러
                            throw (0, app_1.createError)({
                                statusCode: response.status || 500,
                                statusMessage: '알 수 없는 오류가 발생했습니다.'
                            });
                    }
                });
            });
        }
    });
    return {
        provide: {
            api: api
        }
    };
});
