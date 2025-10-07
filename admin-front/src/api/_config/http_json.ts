import axios from 'axios';

const instance = axios.create({});
instance.defaults.headers.common['Access-Control-Allow-Origin'] = '*';
instance.defaults.timeout = 30000; // S3 이미지 업로드 시간 고려하여 30초로 설정
instance.defaults.headers.post['Content-Type'] = 'application/json';
// instance.defaults.headers.post['Content-Type'] =
//     'application/x-www-form-urlencoded';

// 캐싱 방지
instance.defaults.headers.get['Cache-Control'] = 'no-cache';
instance.defaults.headers.get['Pragma'] = 'no-cache';

export default instance;
