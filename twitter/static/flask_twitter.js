const search_input = document.querySelector('.search_input');
const search_submit = document.querySelector('.search_submit');
search_submit.addEventListener(('click'),(event) => {
	callSubmit(event);
})

function callSubmit(event){
	// console.log('有按到了！')
	if(search_input.value.trim()==""){
		// alert("請輸入正確資料");
		event.preventDefault()
	}}
