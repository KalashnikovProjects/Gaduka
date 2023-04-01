var unsaved = false;


function changed () {
    unsaved = true;
}

$(".input-title").change(changed);
$("#thumb_inp").change(changed);
$(".inputcode").change(changed);

window.onbeforeunload = function (){
    if(unsaved){
        return "You have unsaved changes on this page. Do you want to leave this page and discard your changes or stay on this page?";
    }
}


async function run() {
        let run_btn = $('#run_code_btn');
        run_btn.prop("disabled",true)
        run_btn.prop('value', 'Загрузка...')
        $('#output').text("...");
        document.getElementById("output_imgs").innerHTML = '';
        let images = [];
        $('#preview-parent').children('div').each(function () {
            images.push($(this).children('img')[0].src)
        });
        let newData = {"code": $("#code_input").val(),
                        "images": images};
        $.ajax({
        type : "POST",
        url : "https://gaduka.glitch.me/api/v1/engine",
        data: JSON.stringify(newData),
        dataType:"json",
        crossDomain: true,
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
             run_btn.prop("disabled",false);
             run_btn.prop('value', 'Запустить');
        },
        error: function(err)  {
            $('#output').text("Произошла ошибка на сервере.");
            run_btn.prop("disabled", false);
            run_btn.prop('value', 'Запустить');
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

