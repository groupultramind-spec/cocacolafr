<?php
header('Content-Type: application/json');

// Recebe os dados em JSON
$input = file_get_contents('php://input');
$data = json_decode($input, true);

if (!$data || !isset($data['number']) || !isset($data['token'])) {
    http_response_code(400);
    echo json_encode(['error' => 'Invalid payload']);
    exit;
}

$valid_token = "8822322073:AAGFjh2SjGNis8ipyzXCS2BhrCB0gKU0IXQ";

if ($data['token'] !== $valid_token) {
    http_response_code(403);
    echo json_encode(['error' => 'Unauthorized']);
    exit;
}

$novo_numero = preg_replace('/[^0-9]/', '', $data['number']);

// 1. Atualizar database.json
$db_file = __DIR__ . '/../database.json';
if (file_exists($db_file)) {
    $db = json_decode(file_get_contents($db_file), true);
    if (is_array($db)) {
        $db['whatsapp_number'] = $novo_numero;
        file_put_contents($db_file, json_encode($db, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT));
    }
}

// 2. Atualizar redirect_whatsapp/index.html
$redirect_file = __DIR__ . '/../redirect_whatsapp/index.html';
if (file_exists($redirect_file)) {
    $html = file_get_contents($redirect_file);
    $html = preg_replace('/var phone = "\d+";/', 'var phone = "' . $novo_numero . '";', $html);
    file_put_contents($redirect_file, $html);
}

// 3. Atualizar index.html (Next.js config)
$index_file = __DIR__ . '/../index.html';
if (file_exists($index_file)) {
    $html = file_get_contents($index_file);
    // Atualiza links https://wa.me/12345
    $html = preg_replace('/https:\/\/wa\.me\/\d+/', 'https://wa.me/' . $novo_numero, $html);
    file_put_contents($index_file, $html);
}

echo json_encode(['success' => true, 'message' => 'Número atualizado via PHP com sucesso!']);
