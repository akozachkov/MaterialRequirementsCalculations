<%@ page contentType="text/html;charset=UTF-8" language="java" %>
<!DOCTYPE html>
<html lang="en">
<!-- 8/19/2025 20:25-->
<head>
    <meta charset="UTF-8">
    <title>Upload Product File</title>

<link rel="stylesheet" type="text/css" href="styles/MaterialAppStyles.css">



</head>
<body>
    <h1>Upload a Product CSV File</h1>

    <form action="uploadProduct" method="post" enctype="multipart/form-data">
        <label for="file">Choose CSV File:</label>
        <input type="file" name="file" id="file" accept=".csv" required />
        <input type="submit" value="Upload Product" />
    </form>

    <a class="menu-link" href="index.html">🏠 Back to Home</a>
</body>
</html>
