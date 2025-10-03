export const fetchImage = async ( fileName ) => {
    const res = await fetch(`http://localhost:8000/media/download/${fileName}`)
    const imageBlob = await res.blob();
    return URL.createObjectURL(imageBlob)
}