# <!--                <a href="#" id=del>{{page.submit(type="submit", class="btn btn-danger my-4 mx-2")}}</a
    $(document).ready(function() {

   $('#del').bind('click' function() {

      $.ajax({
        data: {
            p_id : $('#id').val(),
            typ : $('#typ').val()
        },
        type : 'POST',
        url : '/process'
      }))

      event.preventDefault();

   });

});