export const shortcuts = [
    {
        text: '오늘',
        value: () => {
            const today = new Date();
            return [today, today];
        }
    },
    {
        text: '어제',
        value: () => {
            const yesterday = new Date();
            yesterday.setDate(yesterday.getDate() - 1);
            return [yesterday, yesterday];
        }
    },
    {
        text: '이번 주',
        value: () => {
            const today = new Date();
            const dayOfWeek = today.getDay();
            const diffToMonday = dayOfWeek === 0 ? -6 : 1 - dayOfWeek; // 일요일인 경우 -6, 그 외에는 월요일까지의 차이

            const startOfWeek = new Date(today);
            startOfWeek.setDate(today.getDate() + diffToMonday);

            return [startOfWeek, today];
        }
    },
    {
        text: '지난 주',
        value: () => {
            const today = new Date();
            const dayOfWeek = today.getDay();
            const diffToMonday = dayOfWeek === 0 ? -6 : 1 - dayOfWeek;

            const startOfLastWeek = new Date(today);
            startOfLastWeek.setDate(today.getDate() + diffToMonday - 7); // 지난주 월요일
            const endOfLastWeek = new Date(startOfLastWeek);
            endOfLastWeek.setDate(startOfLastWeek.getDate() + 6); // 지난주 일요일

            return [startOfLastWeek, endOfLastWeek];
        }
    },
    {
        text: '최근 7일',
        value: () => {
            const end = new Date();
            const start = new Date();
            start.setDate(start.getDate() - 6); // 오늘로부터 6일 전 (오늘 포함 총 7일)
            return [start, end];
        }
    },
    {
        text: '최근 14일',
        value: () => {
            const end = new Date();
            const start = new Date();
            start.setDate(start.getDate() - 13); // 오늘로부터 13일 전 (오늘 포함 총 14일)
            return [start, end];
        }
    },
    {
        text: '최근 30일',
        value: () => {
            const end = new Date();
            const start = new Date();
            start.setDate(start.getDate() - 29); // 오늘로부터 29일 전 (오늘 포함 총 30일)
            return [start, end];
        }
    },
    {
        text: '이번 달',
        value: () => {
            const end = new Date();
            const start = new Date(end.getFullYear(), end.getMonth(), 1); // 이번 달의 첫째 날
            return [start, end];
        }
    },
    {
        text: '지난 달',
        value: () => {
            const start = new Date();
            start.setDate(1); // 현재 달의 첫째 날
            start.setMonth(start.getMonth() - 1); // 지난 달로 이동
            const end = new Date(start.getFullYear(), start.getMonth() + 1, 0); // 지난 달의 마지막 날
            return [start, end];
        }
    },

    {
        text: '1년',
        value: () => {
            const end = new Date(); // 오늘 날짜
            const start = new Date(); // 시작 날짜
            start.setFullYear(start.getFullYear() - 1); // 1년 전으로 이동
            return [start, end];
        }
    },

    {
        text: '전체',
        value: () => {
            const end = ''; // 오늘 날짜
            const start = ''; // 시작 날짜
            return [start, end];
        },
    }

    /*  {
      text: '전체',
      value: () => {
        const end = new Date();
        const start = new Date(end.getFullYear(), end.getMonth(), 1); // 이번 달의 첫째 날
        end.setMonth(end.getMonth() + 1);
        end.setDate(0); // 이번 달의 마지막 날
        return [start, end];
      },
    },*/
];

export function formatDate(inputDate: Date | string, format: string): string {
    const pad = (n: number): string => (n < 10 ? '0' + n : n.toString());

    // 문자열일 경우 Date 객체로 변환
    const date: Date = typeof inputDate === 'string' ? new Date(inputDate) : inputDate;

    // Date 객체 유효성 검사
    if (isNaN(date.getTime())) {
        throw new Error('Invalid date format');
    }

    const replacements: Record<string, string> = {
        'yyyy': date.getFullYear().toString(),
        'MM': pad(date.getMonth() + 1),
        'dd': pad(date.getDate()),
        'HH': pad(date.getHours()),
        'mm': pad(date.getMinutes()),
        'ss': pad(date.getSeconds()),
    };

    return format.replace(/yyyy|MM|dd|HH|mm|ss/g, match => replacements[match]);
}
