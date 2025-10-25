
console.log("defaults_patch loaded");

// frappe.ready(() => {
    frappe.defaults.is_a_user_permission_key = function(key) {
        if (!frappe.defaults.user_permission_keys) {
            return false;
        }
        return frappe.defaults.user_permission_keys.indexOf(key) !== -1;
    };
// });