



// document.addEventListener('DOMContentLoaded', function() {
//   const checkboxes = document.querySelectorAll('.user-checkbox');
//   checkboxes.forEach(function(checkbox) {
//     checkbox.addEventListener('change', function() {
//       if (this.checked) {
//         // Retrieve the user ID from the data attribute
//         const userId = this.getAttribute('data-user-id');
//         // Update the hidden input's value
//         document.getElementById('remove-user-id').value = userId;
//         document.getElementById('deactivate-user-id').value = userId;
//         document.getElementById('reactivate-user-id').value = userId;
//         document.getElementById('make-new-user-admin-id').value = userId;
//         document.getElementById('remove-new-user-admin-id').value = userId;
//       }
//     });
//   });
// });


document.addEventListener('DOMContentLoaded', function() {
  // Retrieve and check the user's role ID
  const roleId = parseInt(document.getElementById('login-user-role-id').value, 10);
  if (roleId > 1) {
    // Select and disable all buttons with the 'user-action-button' class
    document.querySelectorAll('.user-action-button').forEach(button => {
      button.disabled = true;
    });
  }

  // Setup for checkboxes and updating form values based on the selected user
  const checkboxes = document.querySelectorAll('.user-checkbox');
  checkboxes.forEach(function(checkbox) {
    checkbox.addEventListener('change', function() {
      if (this.checked) {
        // Retrieve the user ID from the data attribute
        const userId = this.getAttribute('data-user-id');
        // Update the hidden input's value for various forms
        document.getElementById('remove-user-id').value = userId;
        document.getElementById('deactivate-user-id').value = userId;
        document.getElementById('reactivate-user-id').value = userId;
        document.getElementById('make-new-user-admin-id').value = userId;
        document.getElementById('remove-new-user-admin-id').value = userId;
      }
    });
  });
});
