pytest
if ($LASTEXITCODE -eq 0) {
    allure generate --output allure-report --open .\allure-results
}