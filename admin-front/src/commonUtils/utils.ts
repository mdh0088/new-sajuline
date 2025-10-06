
export const replaceStringToComma = (text, num) => {
    if (text) {
        const regex = new RegExp(`(.{${num}}).*`);
        return text.replace(regex, '$1...');
    } else {
        return "";
    }
}

export const numberComma = (val: number | string): string => {
    const num = parseFloat(String(val));

    // 소수점이 있는 경우에만 2자리까지 자르고, 없는 경우에는 그대로 반환
    const formatted = num % 1 !== 0 ? num.toFixed(2) : String(num);

    // 3자리마다 콤마 추가
    return formatted.replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}


export const toPercentage = (val: number | string): string => {
    const num = parseFloat(String(val));

    // 백분율로 변환하고 소수점 2자리까지만 유지, .00 제거
    return (num ).toFixed(2).replace(/\.00$/, "") + "%";
}

export const formatDate = (date: Date | string, format: string = 'yyyy-MM-dd HH:ss:mm'): string => {
    const d = new Date(date);
    
    if (isNaN(d.getTime())) {
        return '';
    }

    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    const hours = String(d.getHours()).padStart(2, '0');
    const minutes = String(d.getMinutes()).padStart(2, '0');
    const seconds = String(d.getSeconds()).padStart(2, '0');

    return format
        .replace('yyyy', String(year))
        .replace('MM', month)
        .replace('dd', day)
        .replace('HH', hours)
        .replace('mm', minutes)
        .replace('ss', seconds);
}
