

# GitHub CLI api
# https://cli.github.com/manual/gh_api


$alerts = gh api `
    -H "Accept: application/vnd.github+json" `
    -H "X-GitHub-Api-Version: 2022-11-28" `
    "/repos/josverl/micropython-stubber/code-scanning/alerts?state=open&per_page=100" | ConvertFrom-Json 


function dismiss-alerts {
    param (
        $AlertNumber,
        $comment, 
        $Owner = "josverl",
        $Repo = "micropython-stubber"
    )

    gh api --method PATCH `
        -H "Accept: application/vnd.github+json" `
        -H "X-GitHub-Api-Version: 2022-11-28" `
        "/repos/$OWNER/$REPO/code-scanning/alerts/$AlertNumber" `
        -f state='dismissed' `
        -f dismissed_reason='false positive' `
        -f dismissed_comment=$comment | Out-Null

}


foreach ($alert in $alerts ) {
    if ($alert.state -in @("dismissed", "fixed")) {
        write-host -ForegroundColor Cyan $alert.state ":" $alert.html_url
        continue
    }
    if ( $alert.most_recent_instance.location.path.Contains("site-packages/mypy")) {
        dismiss-alerts $alert.number "mypy library is not used in testing"
        write-host -ForegroundColor green "dismissed: " $alert.html_url
    } 
    elseif ( $alert.most_recent_instance.location.path.Contains("typing_extensions")) {
        dismiss-alerts $alert.number "Library is not used in testing"
        write-host -ForegroundColor green "dismissed: " $alert.html_url
    }
    elseif ( $alert.most_recent_instance.location.path.Contains("libcst/_parser")) {
        dismiss-alerts $alert.number "libcst parsing is complex"
        write-host -ForegroundColor green "dismissed: " $alert.html_url
    }
    elseif ( $alert.most_recent_instance.location.path.Contains(".venv/lib/python3.8")) {
        dismiss-alerts $alert.number "not my code"
        write-host -ForegroundColor green "dismissed: " $alert.html_url
    }
    elseif ( $alert.most_recent_instance.location.path.Contains("minified/createstubs")) {
        dismiss-alerts $alert.number "Generated code"
        write-host -ForegroundColor green "dismissed: " $alert.html_url
    }
    elseif ( $alert.most_recent_instance.location.path.Contains("board")) {
        dismiss-alerts $alert.number "report not current"
        write-host -ForegroundColor green "dismissed: " $alert.html_url
    }
    else {
        write-host -ForegroundColor Yellow $alert.state ":" $alert.html_url
        write-host -ForegroundColor White $alert.most_recent_instance.location.path
        
    }

}

