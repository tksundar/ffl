

function delete_confirm() {
  if (confirm("Are you sure yu want to cancel your registration")) {
   document.forms.item(0).submit();
  } else {
   return false
  }
}

