<?php
// used to get mysql database connection
class Database {

    // specify your own database credentials
    private $host = "localhost";
    private $db_name = "sajuline";
    private $username = "sajuline";
    private $password = "sajuline123";
    public $conn;

    // get the database connection
    public function getConnection() {
        $this->conn = null;

        try {
            $dsn = "mysql:host=" . $this->host . ";port=5432;dbname=" . $this->db_name . ";charset=utf8mb4";
            $this->conn = new PDO($dsn, $this->username, $this->password);
            $this->conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

            // $this->conn = new PDO("mysql:host=" . $this->host . ";dbname=" . $this->db_name, $this->username, $this->password);
        } catch(PDOException $exception) {
            echo "Connection error : " . $exception->getMessage();
        }

        return $this->conn;
    }
}
?>

