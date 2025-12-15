<?php
/*

*/
class TelegramAlert{

    var $host_url = 'https://api.telegram.org/bot6062684740:AAFZpODoiegjflv_W5svbKPTJPbQ5OcCsZw/';

    function getUpdates() {
        $url = $this->host_url . 'getUpdates';
        $ch = curl_init();

        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);

        $response = curl_exec($ch);
        curl_close($ch);

        $updates = json_decode($response, true);

        // 중복 제거를 위한 빈 배열 생성
        $uniqueUpdates = array();
        $uniqueChatIds = array();

        foreach ($updates['result'] as $update) {
            $chat_id = $update['message']['chat']['id'];

            // chat_id가 이미 추가되지 않았다면 추가
            if (!in_array($chat_id, $uniqueChatIds)) {
                $uniqueChatIds[] = $chat_id;
                $uniqueUpdates[] = $update;
            }
        }

        return $uniqueUpdates;
    }

    function sendSMS($cont) {

        $uniqueUpdates = $this->getUpdates();
        foreach ($uniqueUpdates as $update) {
            $chat_id = $update['message']['chat']['id'];

            $current_time = date('YmdHis');
            $url = $this->host_url . 'sendMessage';
            $data = array(
                'chat_id' => $chat_id,
                'text' => $cont
            );

            $jsonData = json_encode($data);
            $headers = array(
                'Content-type: application/json'
            );

            $is_post = true;
            $ch = curl_init();

            curl_setopt($ch, CURLOPT_URL, $url);
            curl_setopt($ch, CURLOPT_POST, $is_post);
            curl_setopt($ch, CURLOPT_POSTFIELDS, $jsonData);
            curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
            curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);

            $response = curl_exec($ch);
            /*        if (curl_error($ch)) {
                        // Handle errors if any
                        echo 'Error: (' . curl_errno($ch) . ') ' . curl_error($ch);
                    } else {
                        echo $response;
                    }*/

            curl_close($ch);
            /*
                    $result = json_decode($response);
                    if ($result->code == '0'){
                        $obj = array("isSuc" => TRUE,"no"=>$no,"code"=>$result->code,"cont"=>$msg_content,"template"=>$template_id);
                        return $obj;
                    } else {
                        $obj = array("isSuc" => FALSE,"no"=>$no,"code"=>$result->code,"template"=>$template_id);
                        return $obj;
                    }*/

            //return $response;
        }
    }
}
