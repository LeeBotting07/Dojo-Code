function changeClass(id) {
    var element = document.querySelector("#" + id);
    if (element.style.display === "none") {
        element.style.display = "block";
    } else {
        element.style.display = "none";
    }
}