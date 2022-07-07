<?php
if(isset($_GET['give']) && $_GET['give'] == 'flag'){
    die(file_get_contents('/flag.txt'));
}
?>
<html>
    <head>
        <title>Baby's First Flag</title>
    </head>
    <body>
        <h1>Hello!</h1>
        <p>The flag is definitely not here! <!-- But maybe you should look <a href="/?give=flag">here</a> ? --></p>

        <h3>Database</h3>
        <p>I can connect to the database using credentials: </p>
        <ul>
            <li>Host: db</li>
            <li>User: <?php echo $_ENV['DB_USER']; ?></li>
            <li>Password: <?php echo $_ENV['DB_PASSWORD']; ?></li>
        </ul>
    </body>
</html>