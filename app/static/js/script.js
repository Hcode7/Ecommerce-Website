
// JavaScript for Menu Toggle    
document.getElementById('menu-btn').addEventListener('click', function() {
    document.getElementById('mobile-menu').classList.toggle('hidden');
});

let counter = countcart;

function count() {
    counter++;
    document.querySelector('h4').innerHTML = counter;
}


function removecount() {
    document.querySelector('h4').innerHTML = counter;
}

