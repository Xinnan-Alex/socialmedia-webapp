const commentReplyToggle = (parent_id) => {
  const row = document.getElementById(parent_id);
  row.classList.toggle("d-none");
};

const showNotificationToggle = () => {
  const container = document.getElementById("notification-container");
  container.classList.toggle("d-none");
};

const getCookie = (name) => {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
};

const removeNotification = (removeNotificationURL, redirectURL) => {
  const csrftoken = getCookie("csrftoken");
  const xmlHttp = new XMLHttpRequest();
  xmlHttp.onreadystatechange = () => {
    if (xmlHttp.readyState == XMLHttpRequest.DONE) {
      xmlHttp.status == 200
        ? window.location.replace(redirectURL)
        : alert("There was an error");
    }
  };

  xmlHttp.open("DELETE", removeNotificationURL, true);
  xmlHttp.setRequestHeader("X-CSRFToken", csrftoken);
  xmlHttp.send();
};
