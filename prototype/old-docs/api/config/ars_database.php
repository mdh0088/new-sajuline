<?php
// used to get MSSQL database connection
class ARS_database{

    // specify your own database credentials
    private $server = "175.117.146.168:2866";
    private $user = "peopleline";
    private $pass = "peopleline##";
    private $db = "ars";
    public $conn;

    // get the database connection
    public function getConnection(){

        $this->conn = null;

        $this->conn = mssql_connect($this->server, $this->user, $this->pass);
        if (!$this->conn) {
            die('Something went wrong while connecting to MSSQL');
        }
        mssql_select_db($this->db, $this->conn);

        return $this->conn;
    }
}
?>
