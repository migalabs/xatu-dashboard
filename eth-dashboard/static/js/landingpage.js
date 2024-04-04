const leftBox = document.getElementById('left-box');
const rightBox = document.getElementById('right-box');
const imageLeft = document.querySelector('.image-left img');
const imageRight = document.querySelector('.image-right img');

function handleResize() {
  if (window.innerWidth < 830) {
    imageLeft.style.transform = '';
    imageLeft.style.opacity = '1';
    imageRight.style.transform = '';
    imageRight.style.opacity = '1';
  } else {
    imageLeft.style.opacity = '0.8';
    imageRight.style.opacity = '0.8';
  }
}

function handleMouseOverLeft() {
  if (window.innerWidth >= 830) {
    imageLeft.style.transform = 'scale(1.1)';
    imageLeft.style.opacity = '1';
  }
}

function handleMouseOutLeft() {
  if (window.innerWidth >= 830) {
    imageLeft.style.transform = 'scale(1)';
    imageLeft.style.opacity = '0.8';
  }
}

function handleMouseOverRight() {
  if (window.innerWidth >= 830) {
    imageRight.style.transform = 'scale(1.1)';
    imageRight.style.opacity = '1';
  }
}

function handleMouseOutRight() {
  if (window.innerWidth >= 830) {
    imageRight.style.transform = 'scale(1)';
    imageRight.style.opacity = '0.8';
  }
}

window.addEventListener('resize', handleResize);
window.addEventListener('load', handleResize);
leftBox.addEventListener('mouseover', handleMouseOverLeft);
leftBox.addEventListener('mouseout', handleMouseOutLeft);
rightBox.addEventListener('mouseover', handleMouseOverRight);
rightBox.addEventListener('mouseout', handleMouseOutRight);
