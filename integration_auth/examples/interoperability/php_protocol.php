<?php

declare(strict_types=1);

function encode_rfc3986(string $value): string
{
    return rawurlencode($value);
}

function canonical_query(array $pairs): string
{
    $encoded = array_map(
        static fn(array $pair): array => [encode_rfc3986($pair[0]), encode_rfc3986($pair[1])],
        $pairs,
    );
    usort($encoded, static fn(array $a, array $b): int => $a <=> $b);
    return implode('&', array_map(
        static fn(array $pair): string => $pair[0] . '=' . $pair[1],
        $encoded,
    ));
}

function canonical_request(array $vector): string
{
    $query = canonical_query($vector['query']);
    $pathAndQuery = $query === '' ? $vector['path'] : $vector['path'] . '?' . $query;
    return implode("\n", [
        $vector['method'],
        $pathAndQuery,
        (string) $vector['timestamp'],
        $vector['nonce'],
        hash('sha256', $vector['body']),
    ]);
}

$vectors = json_decode(file_get_contents(__DIR__ . '/vectors.json'), true, flags: JSON_THROW_ON_ERROR);
$results = [];
foreach (['inbound', 'outbound'] as $name) {
    $vector = $vectors[$name];
    $query = canonical_query($vector['query']);
    $bodyHash = hash('sha256', $vector['body']);
    $signature = hash_hmac('sha256', canonical_request($vector), $vector['secret']);
    $results[$name] = hash_equals($vector['signature'], $signature)
        && $query === $vector['canonical_query']
        && $bodyHash === $vector['body_sha256'];
}

echo json_encode($results, JSON_THROW_ON_ERROR | JSON_UNESCAPED_SLASHES) . PHP_EOL;
if (in_array(false, $results, true)) {
    exit(1);
}
