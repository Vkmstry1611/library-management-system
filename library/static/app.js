let book_select = document.getElementById('book_name1');
let member_select = document.getElementById('member_name1');

// fetches the member list for returning the book (only runs if return modal is on the page)
if (book_select && member_select) {
    book_select.addEventListener('change', (e) => {
        let book_id = book_select.value;
        member_select.innerHTML = '<option selected>Members</option>';

        fetch('/book/' + book_id).then(function (response) {
            response.json().then(function (data) {
                for (let member of data.members) {
                    member_select.innerHTML += '<option value="' + member.id + '">' + member.member_name + '</option>';
                }
            });
        });
    });
}
