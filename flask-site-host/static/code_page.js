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
        let images = []
        $('#preview-parent').children('div').each(function () {
            images.push($(this).children('img')[0].src)
        });
        let newData = {"code": $("#code_input").val(),
                        "images": images};
        console.log(images)
        $.ajax({
        type : "POST",
        url : "/api/v1/engine",
        data: JSON.stringify(newData),
        dataType:"json",
        contentType:"application/json",
        success: function(result) {
             text_output = result['result_text']
             if (text_output === '') {
                 text_output = 'Код ничего не вывел.'
             }
             $('#output').text(text_output);
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
                 img.src = `data:image/png;base64,${result['result_imgs'][data_i].replace(/['"]+/g, '')}`;
                 img.alt = 'Результат выполнения программы';
             }
        }
})}


var dataTransfer = new DataTransfer()

function changedInput () {

  let files = window.input.files

  for (let i = 0; i < files.length; i++) {
    dataTransfer.items.add(files[i])

    let reader, preview, previewImage;
    reader = new FileReader();

    preview = document.createElement('div');
    previewImage = document.createElement('img');
    deleteButton = document.createElement('button');
    orderInput = document.createElement('input');

    preview.classList.add('preview');
    document.querySelector('#preview-parent').appendChild(preview);
    deleteButton.setAttribute('data-index', i);
    deleteButton.setAttribute('onclick', 'deleteImage(this)');
    deleteButton.className = 'btn btn-secondary';
    deleteButton.innerText = 'Удалить';
    orderInput.type = 'hidden';
    orderInput.name = 'images_order[' + files[i].name + ']';

    preview.appendChild(previewImage);
    preview.appendChild(deleteButton);
    preview.appendChild(orderInput);

    reader.readAsDataURL(files[i]);
    reader.onloadend = () => {
      previewImage.src = reader.result
    }
  }

  updateOrder()
  window.input.files = dataTransfer.files
}

const updateOrder = () => {
  let orderInputs = document.querySelectorAll('input[name^="images_order"]');
  let deleteButtons = document.querySelectorAll('button[data-index]');
  for (let i = 0; i < orderInputs.length; i++) {
    orderInputs[i].value = [i];
    deleteButtons[i].dataset.index = [i];

    deleteButtons[i].innerText = 'Удалить';
  }
}

const deleteImage = (item) => {
  dataTransfer.items.remove(item.dataset.index)
  window.input.files = dataTransfer.files
  item.parentNode.remove()
  updateOrder()
}


function loadPreview() {
    window.input = document.querySelector('#images_code')
    const el = document.getElementById('preview-parent')
    new Sortable(el, {
    animation: 150,

    onEnd: (event) => {
        updateOrder()
    }
    })
}

