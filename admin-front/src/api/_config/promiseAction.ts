import axios, { AxiosResponse, AxiosError  } from 'axios';

// promiseAll 함수 - 여러 호출 중 하나가 오류가 나와도 전체 오류로 처리
export async function promiseAll(requests: Promise<AxiosResponse<any>>[]): Promise<{ success: boolean; value?: any; uri?: string; reason?: string }[]> {
    try {
        const responses = await Promise.all(requests);
        const resultData = responses.map((response) => {
            return {
                success: true,
                value: response.data,
                uri: response.config.url
            };
        });
        return resultData;
    } catch (error: any) {
        // 오류 발생 시 처리
        return [{
            success: false,
            reason: error.response.data.detail,
            uri: error.config?.url
        }];
    }
}


// promiseSettled 함수 - 성공 또는 실패한 모든 요청 결과를 반환
export async function promiseSettled(requests: Promise<AxiosResponse<any>>[]): Promise<{ success: boolean; value?: any; uri?: string; reason?: string }[]> {
    const results:any = await Promise.allSettled(requests);

    const resultData = results.map(result => {
        if (result.status === 'fulfilled') {
            // result.value는 AxiosResponse 타입으로 처리
            const element = result.value as AxiosResponse;
            return {
                success: true,
                value: element.data,
                uri: element.config.url
            };
        } else {
            // result.reason은 unknown 타입이므로 먼저 any로 캐스팅한 후 AxiosError 체크
            const error = result.reason; // 여기서 에러 객체를 가져와야 함
            if (axios.isAxiosError(error)) {
                return {
                    success: false,
                    reason: error.response.data.detail,
                    uri: error.config?.url // optional chaining 사용
                };
            } else {
                return {
                    success: false,
                    reason: 'Unknown error occurred',
                    uri: ''
                };
            }
        }
    });

    return resultData;
}