$(document).ready(function() {
    // initialize with defaults

    // with plugin options
    $("#input-id").fileinput({language: "ru", allowedFileExtensions: ["jpg", "png", "gif"]});
});


function toBase64(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => resolve(reader.result);
      reader.onerror = error => reject(error);
    });
  }

  async function tobase64Handler(files) {
    const filePathsPromises = [];
    files.forEach(file => {
      filePathsPromises.push(this.toBase64(file));
    });
    const filePaths = await Promise.all(filePathsPromises);
    return filePaths;
  }


async function run() {
        let data = {"code": $("#code_input").val(),
                    "images": $("#images_code").prop('files')};
        let images = await tobase64Handler(Array.from(data['images']));
        let newData  = {"code": data['code'],
                         "images": images};
        $.ajax({
        type : "POST",
        url : "/api/v1/engine",
        data: JSON.stringify(newData),
        dataType:"json",
        contentType:"application/json",
        success: function(result) {
             $('#output').text(result['result_text']);
             let imgsDiv = document.getElementById("output_imgs");
             imgsDiv.innerHTML = '';
             let flag = true;
             for (let data_i=0;data_i < result['result_imgs'].length;data_i++) {
                 let div = imgsDiv.appendChild(document.createElement('div'));
                 let b = "carousel-item"
                 if (flag) {b += ' active'; flag=false}
                 div.className = b;

                 let img = div.appendChild(document.createElement('img'));
                 img.className = 'img-carousel';
                 console.log(`data:image/png;base64,${result['result_imgs'][data_i].replace(/['"]+/g, '')}`);
                 img.src = `data:image/png;base64,${result['result_imgs'][data_i].replace(/['"]+/g, '')}`;
                 img.alt = 'Результат выполнения программы';
             }
        }
})}
