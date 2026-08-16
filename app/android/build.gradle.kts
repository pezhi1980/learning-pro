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
    afterEvaluate {
        if (project.name == "url_launcher_android") {
            pluginManager.apply("com.android.built-in-kotlin")
        }
    }
}

tasks.register<Delete>("clean") {
    delete(rootProject.layout.buildDirectory)
}
