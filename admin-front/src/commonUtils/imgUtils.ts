export const createFormData = (imgFileList) => {
    const formData = new FormData();
    imgFileList.forEach(file => {
        if (file.raw) {
            formData.append("imgUpload", file.raw);
        }
    });
    return formData;
}
