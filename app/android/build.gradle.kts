allprojects {
    repositories {
        google()
        mavenCentral()
    }
}

val newBuildDir = file("C:/build_lang")
rootProject.layout.buildDirectory.set(newBuildDir)

subprojects {
    project.layout.buildDirectory.set(file("C:/build_lang/${project.name}"))
}
subprojects {
    project.evaluationDependsOn(":app")
}

subprojects {
    if (project.name == "url_launcher_android") {
        if (project.state.executed) {
            pluginManager.apply("com.android.built-in-kotlin")
        } else {
            afterEvaluate {
                pluginManager.apply("com.android.built-in-kotlin")
            }
        }
    }
}
