<%@ page contentType="text/html;charset=UTF-8" language="java" %>
<html>
<!-- 8/19/2025 14:35-->
<head>
    <title>Upload Product</title>
</head>
<body>
    <h2>Upload a Product CSV File</h2>
    <form action="uploadProduct" method="post" enctype="multipart/form-data">
        <label for="file">Choose CSV File:</label>
        <input type="file" name="file" id="file" accept=".csv" required />
        <br><br>
        <input type="submit" value="Upload" />
    </form>
    <br>
    <a href="index.html">Back to Home</a>
</body>
</html>
