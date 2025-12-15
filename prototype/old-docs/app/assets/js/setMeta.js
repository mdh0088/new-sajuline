function setMeta(params) {
    params.description = params.description
        .replace(/(?:\r\n|\r|\n)/g, '')
        .replace(/&nbsp;/gi, '')
        .replace(/&rsquo;/gi, '')
        .replace(/&lsquo;/gi, '')
        .replace(/\t/gi, '')
        .replace(/&#39/gi, '');

    const description = params.description.length > 300 ? params.description.substring(0, 300) : params.description;

    let keyword = '';
    if (!params.keyword) {
        keyword = '사주로, 사주타로, 타로, 운세, 사주, 꿈해몽 전화상담';
    } else {
        keyword = params.keyword.length > 300 ? params.keyword.substring(0, 300) : params.keyword;
    }

    try {
        document.title = params.title;
        document.querySelector('meta[name="description"]').setAttribute('content', description);
        document.querySelector('meta[name="og:title"]').setAttribute('content', params.title);
        document.querySelector('meta[name="og:description"]').setAttribute('content', description);
        document.querySelector('meta[name="twitter:title"]').setAttribute('content', params.title);
        document.querySelector('meta[name="twitter:description"]').setAttribute('content', description);
        document.querySelector('meta[name="keywords"]').setAttribute('content', keyword);
        document.querySelector('meta[name="og:url"]').setAttribute('content', params.url);
        document.querySelector('meta[name="twitter:url"]').setAttribute('content', params.url);

    } catch (err) {
        console.log('meta throw');
    }
}
