/*!
* Start Bootstrap - Freelancer v7.0.5 (https://startbootstrap.com/theme/freelancer)
* Copyright 2013-2021 Start Bootstrap
* Licensed under MIT (https://github.com/StartBootstrap/startbootstrap-freelancer/blob/master/LICENSE)
*/
//
// Scripts
// 
var acc = document.getElementsByClassName("accordion-button");
var i;

for (i = 0; i < acc.length; i++) {
  acc[i].addEventListener("click", function() {
    /* Toggle between adding and removing the "active" class,
    to highlight the button that controls the panel */
    this.classList.toggle("active");

    /* Toggle between hiding and showing the active panel */
    var panel = this.nextElementSibling;
    alert(1)
    if (panel.style.display === "block") {
      panel.style.display = "none";
    } else {
      panel.style.display = "block";
    }
  });
} 
window.addEventListener('DOMContentLoaded', event => {

    // Navbar shrink function
    var navbarShrink = function () {
        const navbarCollapsible = document.body.querySelector('#mainNav');
        if (!navbarCollapsible) {
            return;
        }
        if (window.scrollY === 0) {
            navbarCollapsible.classList.remove('navbar-shrink')
        } else {
            navbarCollapsible.classList.add('navbar-shrink')
        }

    };

    // Shrink the navbar 
    navbarShrink();

    // Shrink the navbar when page is scrolled
    document.addEventListener('scroll', navbarShrink);

    // Activate Bootstrap scrollspy on the main nav element
 /*    const mainNav = document.body.querySelector('#mainNav');
    if (mainNav) {
        new bootstrap.ScrollSpy(document.body, {
            target: '#mainNav',
            offset: 72,
        });
    }; */

    // Collapse responsive navbar when toggler is visible
    const navbarToggler = document.body.querySelector('.navbar-toggler');
    const responsiveNavItems = [].slice.call(
        document.querySelectorAll('#navbarResponsive .nav-link')
    );
    responsiveNavItems.map(function (responsiveNavItem) {
        responsiveNavItem.addEventListener('click', () => {
            if (window.getComputedStyle(navbarToggler).display !== 'none') {
                navbarToggler.click();
            }
        });
    });

});

// submit and add fragment buttons
let addFragmentFormBtn = document.querySelector("#data-formset-add");
let fragmentForm = document.querySelectorAll(".fragment-form");
let mainForm = document.querySelector("#Form-container");
let totalForms = document.querySelector("#id_form-TOTAL_FORMS");

let formCount = fragmentForm.length - 1;
var str = document.getElementById("num").innerHTML;
let countNum = parseInt(str)


addFragmentFormBtn.addEventListener("click", function (event) {
    alert(1)
    updateNumber();
});


function updateNumber() {
    var elems = document.querySelectorAll('h2');
    if (elems.length) { 
      for(var i=0; i<elems.length; i++){
          a=i+1
        elems[i].innerHTML = 'Fragment #'+a;
      }
    }
    
} 

mainForm.addEventListener("click", function (event) {
    if (event.target.classList.contains("delete-fragment-form")) {
        event.preventDefault();
        if(countNum < 3){
            alert('At least two fragments are requiered!');
        }
        else{
            countNum -= 1;
            event.target.parentElement.remove();
            updateNumber();
            //formCount--;
            totalForms.setAttribute('value', `${formCount + 1}`);}
            //alert(event.target.parentElement.filter(':checkbox'))
            //event.target.parentElement.filter(':checkbox').prop('checked',true);}
            
            //updateForms();}
    }
});






