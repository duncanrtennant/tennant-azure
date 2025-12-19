// Wait for the DOM to be loaded before attaching event handlers
document.addEventListener("DOMContentLoaded", () => {
	const incrementButton = document.getElementById("incrementButton");
	const incrementButton2 = document.getElementById("incrementButton2");
	const counterSpan = document.getElementById("counter");
	const progressBar = document.getElementById("progressBar");

	// Initialize the counter
	let counter = 0; // Start from 0 each time the page loads
	let percentTo50 = 0;
	counterSpan.innerText = counter; // Display the initial value

	// When the button is clicked, increment the counter
	incrementButton.addEventListener("click", () => {
		counter += 1;
		percentTo50 = counter*2;
		counterSpan.innerText = counter; // Update the displayed counter
		progressBar.style = "width:"+percentTo50+"%";
		if (percentTo50<25){
			progressBar.className="progress-bar bg-danger";
		} else if (percentTo50<75){
			progressBar.className="progress-bar bg-warning";
		} else {
			progressBar.className="progress-bar bg-success";
		}
	});

	incrementButton2.addEventListener("click", () => {
		counter += 1;
		percentTo50 = counter*2;
		counterSpan.innerText = counter; // Update the displayed counter
		progressBar.style = "width:"+percentTo50+"%";
	});
});
