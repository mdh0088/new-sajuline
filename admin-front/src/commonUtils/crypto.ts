import CryptoJS from 'crypto-js';

// 키와 IV 정의 (타입 명시)
const key = CryptoJS.enc.Utf8.parse('___dmcmedia___adserver___key____'); // 16, 24, 또는 32 바이트 키
const iv = CryptoJS.enc.Utf8.parse('dmcmediakeyadsvr'); // 16 바이트 IV

// 암호화 함수
export function encrypteTarget(pw: string): string {
    const encrypted = CryptoJS.AES.encrypt(pw, key, {
        iv: iv,
        mode: CryptoJS.mode.CBC,
        padding: CryptoJS.pad.Pkcs7
    });
    return encrypted.toString();
}

// 복호화 함수
export function decrypteTarget(encrypted: string): string {
    const decrypted = CryptoJS.AES.decrypt(encrypted, key, {
        iv: iv,
        mode: CryptoJS.mode.CBC,
        padding: CryptoJS.pad.Pkcs7
    });
    return CryptoJS.enc.Utf8.stringify(decrypted);
}
